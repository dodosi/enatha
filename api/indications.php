<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

requireAuth();

$q = trim((string) ($_GET['q'] ?? ''));
$path = dirname(__DIR__) . '/database/dictionaries/who_icd11_clinical_conditions.csv';
if (!is_readable($path)) {
    jsonResponse(['success' => false, 'message' => 'Clinical conditions dictionary CSV not found'], 500);
}

$choices = [];
$fh = fopen($path, 'rb');
if ($fh === false) {
    jsonResponse(['success' => false, 'message' => 'Unable to read clinical conditions dictionary'], 500);
}

$header = fgetcsv($fh);
$idIdx = array_search('condition_id', $header ?: [], true);
$nameIdx = array_search('condition_name_standardized', $header ?: [], true);
$domainIdx = array_search('clinical_domain', $header ?: [], true);
$synIdx = array_search('search_terms_synonyms', $header ?: [], true);

if ($idIdx === false || $nameIdx === false) {
    fclose($fh);
    jsonResponse(['success' => false, 'message' => 'Invalid clinical conditions dictionary header'], 500);
}

$qLower = mb_strtolower($q);
while (($row = fgetcsv($fh)) !== false) {
    $id = trim((string) ($row[$idIdx] ?? ''));
    $name = trim((string) ($row[$nameIdx] ?? ''));
    if ($id === '' || $name === '') {
        continue;
    }
    $domain = trim((string) ($row[$domainIdx] ?? ''));
    $syn = trim((string) ($row[$synIdx] ?? ''));
    $hay = mb_strtolower($id . ' ' . $name . ' ' . $domain . ' ' . $syn);
    if ($qLower !== '' && mb_strpos($hay, $qLower) === false) {
        continue;
    }
    $text = $domain !== '' ? ($domain . ': ' . $name) : $name;
    $choices[] = ['value' => $id, 'text' => $text];
}

fclose($fh);

$choices[] = [
    'value' => 'IND_OTHER',
    'text' => 'Other infection/clinical indication — specify',
];

jsonResponse(['success' => true, 'choices' => $choices]);
