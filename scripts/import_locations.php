<?php
/**
 * Import Rwanda administrative locations from CSV.
 *
 * CSV columns:
 * province,district,sector,cell,village
 *
 * Usage:
 * php scripts/import_locations.php database/locations/rwanda_locations_sample.csv
 */

if (php_sapi_name() !== 'cli') {
    http_response_code(403);
    echo 'This script must be run from the command line: php scripts/import_locations.php path/to/file.csv';
    exit(1);
}

require_once dirname(__DIR__) . '/config/database.php';

$csvPath = $argv[1] ?? dirname(__DIR__) . '/database/locations/rwanda_locations_sample.csv';
if (!is_file($csvPath)) {
    echo "CSV file not found: {$csvPath}\n";
    exit(1);
}

$handle = fopen($csvPath, 'r');
if ($handle === false) {
    echo "Cannot open CSV file: {$csvPath}\n";
    exit(1);
}

$db = getDb();
$db->beginTransaction();

try {
    $header = fgetcsv($handle);
    if (!$header) {
        throw new RuntimeException('CSV file is empty.');
    }

    $expected = ['province', 'district', 'sector', 'cell', 'village'];
    $header = array_map('trim', $header);
    if ($header !== $expected) {
        throw new RuntimeException('CSV header must be: ' . implode(',', $expected));
    }

    $count = 0;
    while (($row = fgetcsv($handle)) !== false) {
        $row = array_map('trim', $row);
        if (count($row) < 5 || implode('', $row) === '') {
            continue;
        }

        [$province, $district, $sector, $cell, $village] = $row;
        if ($province === '' || $district === '' || $sector === '' || $cell === '' || $village === '') {
            continue;
        }

        $provinceId = upsertLocation($db, 'provinces', null, null, $province);
        $districtId = upsertLocation($db, 'districts', 'province_id', $provinceId, $district);
        $sectorId = upsertLocation($db, 'sectors', 'district_id', $districtId, $sector);
        $cellId = upsertLocation($db, 'cells', 'sector_id', $sectorId, $cell);
        upsertLocation($db, 'villages', 'cell_id', $cellId, $village);

        $count++;
    }

    $db->commit();
    fclose($handle);
    echo "Imported {$count} location rows successfully.\n";
} catch (Exception $e) {
    $db->rollBack();
    fclose($handle);
    echo 'Import failed: ' . $e->getMessage() . "\n";
    exit(1);
}

function upsertLocation(PDO $db, string $table, ?string $parentColumn, ?int $parentId, string $name): int
{
    if ($parentColumn === null) {
        $select = $db->prepare("SELECT id FROM {$table} WHERE name = ? LIMIT 1");
        $select->execute([$name]);
        $existing = $select->fetch();

        if ($existing) {
            return (int) $existing['id'];
        }

        $insert = $db->prepare("INSERT INTO {$table} (name) VALUES (?)");
        $insert->execute([$name]);
        return (int) $db->lastInsertId();
    }

    $select = $db->prepare("SELECT id FROM {$table} WHERE {$parentColumn} = ? AND name = ? LIMIT 1");
    $select->execute([$parentId, $name]);
    $existing = $select->fetch();

    if ($existing) {
        return (int) $existing['id'];
    }

    $insert = $db->prepare("INSERT INTO {$table} ({$parentColumn}, name) VALUES (?, ?)");
    $insert->execute([$parentId, $name]);
    return (int) $db->lastInsertId();
}
