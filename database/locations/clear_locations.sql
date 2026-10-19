-- Select your app database in phpMyAdmin LEFT panel BEFORE running this file.
-- Do not include USE enatha_survey (hosting DB name differs).
-- Empty Rwanda administrative location tables (keep health_facilities).
-- Run in phpMyAdmin on your app database (select it first in phpMyAdmin), or:
--   Import in phpMyAdmin after selecting your database


DELETE FROM villages;
DELETE FROM cells;
DELETE FROM sectors;
DELETE FROM districts;
DELETE FROM provinces;
