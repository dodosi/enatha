<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

requireAuth();

$district = trim((string) ($_GET['district'] ?? ''));

$sql = 'SELECT facility_code, name, facility_type, facility_level, district_name
        FROM health_facilities
        WHERE status = ?';
$params = ['active'];

if ($district !== '') {
    $sql .= ' AND district_name = ?';
    $params[] = $district;
}

$sql .= ' ORDER BY district_name, facility_level, name';

try {
    $stmt = getDb()->prepare($sql);
    $stmt->execute($params);
    $rows = $stmt->fetchAll();
} catch (Throwable $e) {
    jsonResponse([
        'success' => false,
        'message' => 'Health facilities table is not available. Import database/locations/health_facilities_seed.sql',
    ], 500);
}

$choices = [];
foreach ($rows as $row) {
    $label = $row['facility_code'] . ' — ' . $row['name']
        . ' (' . $row['district_name'] . ', ' . $row['facility_type'] . ' ' . $row['facility_level'] . ')';
    $choices[] = [
        'value' => $row['facility_code'],
        'text'  => $label,
    ];
}

jsonResponse([
    'success' => true,
    'choices' => $choices,
]);
