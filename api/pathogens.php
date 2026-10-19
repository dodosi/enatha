<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

requireAuth();

$q = trim((string) ($_GET['q'] ?? ''));
$path = dirname(__DIR__) . '/database/dictionaries/pathogen_dictionary.csv';
if (!is_readable($path)) {
    jsonResponse(['success' => false, 'message' => 'Pathogen dictionary CSV not found'], 500);
}

$choices = [];
$fh = fopen($path, 'rb');
if ($fh === false) {
    jsonResponse(['success' => false, 'message' => 'Unable to read pathogen dictionary'], 500);
}

$header = fgetcsv($fh);
$idIdx = array_search('pathogen_id', $header ?: [], true);
$nameIdx = array_search('pathogen_name_standardized', $header ?: [], true);
$synIdx = array_search('search_terms', $header ?: [], true);

if ($idIdx === false || $nameIdx === false) {
    fclose($fh);
    jsonResponse(['success' => false, 'message' => 'Invalid pathogen dictionary header'], 500);
}

$qLower = mb_strtolower($q);
while (($row = fgetcsv($fh)) !== false) {
    $id = trim((string) ($row[$idIdx] ?? ''));
    $name = trim((string) ($row[$nameIdx] ?? ''));
    if ($id === '' || $name === '') {
        continue;
    }
    $syn = trim((string) ($row[$synIdx] ?? ''));
    $hay = mb_strtolower($id . ' ' . $name . ' ' . $syn);
    if ($qLower !== '' && mb_strpos($hay, $qLower) === false) {
        continue;
    }
    $choices[] = ['value' => $id, 'text' => $name];
}
fclose($fh);

jsonResponse(['success' => true, 'choices' => $choices]);
