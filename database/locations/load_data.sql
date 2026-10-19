-- DATA ONLY — paste after tables exist
-- phpMyAdmin: select u924861691_enatha_survey → SQL → Go

DELETE FROM villages;
DELETE FROM cells;
DELETE FROM sectors;
DELETE FROM districts;
DELETE FROM provinces;

INSERT INTO provinces (name, status) VALUES
('Kigali City', 'active'),
('Eastern Province', 'active'),
('Northern Province', 'active');

INSERT INTO districts (province_id, name, status)
SELECT id, 'Gasabo', 'active' FROM provinces WHERE name = 'Kigali City';
INSERT INTO districts (province_id, name, status)
SELECT id, 'Bugesera', 'active' FROM provinces WHERE name = 'Eastern Province';
INSERT INTO districts (province_id, name, status)
SELECT id, 'Gakenke', 'active' FROM provinces WHERE name = 'Northern Province';

INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Kimironko', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo';
INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Kinyinya', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo';
INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Gisozi', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo';
INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Remera', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo';
INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Nyamata', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera';
INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Mayange', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera';
INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Cyabingo', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke';
INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Nemba', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke';
INSERT INTO sectors (district_id, name, status)
SELECT d.id, 'Ruli', 'active' FROM districts d JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke';

INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Kibagabaga', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kimironko';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Murama', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kinyinya';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Kagugu', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kinyinya';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Musezero', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Gisozi';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Rukiri II', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Remera';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Unspecified', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Remera';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Kayumba', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Nyamata y''Umujyi', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Nyamata/Town', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Gakamba', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Mayange';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Kibenga', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Mayange';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Muramba', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Cyabingo';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Mucaca', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Gahinga', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Gisozi', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba';
INSERT INTO cells (sector_id, name, status)
SELECT s.id, 'Ruli Centre', 'active' FROM sectors s JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Ruli';

INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Rugero', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kimironko' AND c.name = 'Kibagabaga';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Taba', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kinyinya' AND c.name = 'Murama';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Kinyinya' AND c.name = 'Kagugu';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Gisozi' AND c.name = 'Musezero';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Remera' AND c.name = 'Rukiri II';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Kigali City' AND d.name = 'Gasabo' AND s.name = 'Remera' AND c.name = 'Unspecified';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND c.name = 'Kayumba';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND c.name = 'Nyamata y''Umujyi';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Nyamata' AND c.name = 'Nyamata/Town';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Mayange' AND c.name = 'Gakamba';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Eastern Province' AND d.name = 'Bugesera' AND s.name = 'Mayange' AND c.name = 'Kibenga';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Gahama', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Cyabingo' AND c.name = 'Muramba';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Cyahafi', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND c.name = 'Mucaca';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Bukurura', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND c.name = 'Gahinga';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Muganwa', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND c.name = 'Gisozi';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Nemba' AND c.name = 'Mucaca';
INSERT INTO villages (cell_id, name, status)
SELECT c.id, 'Unspecified', 'active' FROM cells c JOIN sectors s ON s.id = c.sector_id JOIN districts d ON d.id = s.district_id JOIN provinces p ON p.id = d.province_id WHERE p.name = 'Northern Province' AND d.name = 'Gakenke' AND s.name = 'Ruli' AND c.name = 'Ruli Centre';

SELECT 'provinces' AS t, COUNT(*) AS n FROM provinces
UNION ALL SELECT 'districts', COUNT(*) FROM districts
UNION ALL SELECT 'sectors', COUNT(*) FROM sectors
UNION ALL SELECT 'cells', COUNT(*) FROM cells
UNION ALL SELECT 'villages', COUNT(*) FROM villages;
