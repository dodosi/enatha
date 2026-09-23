<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

requireAuth();

$level = $_GET['level'] ?? '';
$parentId = isset($_GET['parent_id']) ? (int) $_GET['parent_id'] : 0;

$queries = [
    'provinces' => [
        'sql' => 'SELECT id, name FROM provinces WHERE status = ? ORDER BY name',
        'params' => ['active'],
        'requires_parent' => false,
    ],
    'districts' => [
        'sql' => 'SELECT id, name FROM districts WHERE province_id = ? AND status = ? ORDER BY name',
        'params' => [$parentId, 'active'],
        'requires_parent' => true,
    ],
    'sectors' => [
        'sql' => 'SELECT id, name FROM sectors WHERE district_id = ? AND status = ? ORDER BY name',
        'params' => [$parentId, 'active'],
        'requires_parent' => true,
    ],
    'cells' => [
        'sql' => 'SELECT id, name FROM cells WHERE sector_id = ? AND status = ? ORDER BY name',
        'params' => [$parentId, 'active'],
        'requires_parent' => true,
    ],
    'villages' => [
        'sql' => 'SELECT id, name FROM villages WHERE cell_id = ? AND status = ? ORDER BY name',
        'params' => [$parentId, 'active'],
        'requires_parent' => true,
    ],
];

if (!isset($queries[$level])) {
    jsonResponse(['success' => false, 'message' => 'Invalid location level'], 400);
}

$query = $queries[$level];
if ($query['requires_parent'] && $parentId <= 0) {
    jsonResponse(['success' => true, 'choices' => []]);
}

$stmt = getDb()->prepare($query['sql']);
$stmt->execute($query['params']);

$choices = [];
foreach ($stmt->fetchAll() as $row) {
    $choices[] = [
        'value' => (int) $row['id'],
        'text'  => $row['name'],
    ];
}

jsonResponse([
    'success' => true,
    'level'   => $level,
    'choices' => $choices,
]);
