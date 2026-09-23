<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

requireAuth();

$q = trim((string) ($_GET['q'] ?? ''));
$limit = isset($_GET['limit']) ? (int) $_GET['limit'] : 300;
if ($limit < 1 || $limit > 500) {
    $limit = 300;
}

$path = dirname(__DIR__) . '/database/dictionaries/who_antimicrobial_dictionary.csv';
if (!is_readable($path)) {
    jsonResponse(['success' => false, 'message' => 'Antimicrobial dictionary CSV not found'], 500);
}

$choices = [];
$fh = fopen($path, 'rb');
if ($fh === false) {
    jsonResponse(['success' => false, 'message' => 'Unable to read antimicrobial dictionary'], 500);
}

$header = fgetcsv($fh);
$nameIdx = array_search('antimicrobial_name_standardized', $header ?: [], true);
$atcIdx = array_search('atc_code', $header ?: [], true);
$awareIdx = array_search('aware_category', $header ?: [], true);

if ($nameIdx === false) {
    fclose($fh);
    jsonResponse(['success' => false, 'message' => 'Invalid antimicrobial dictionary header'], 500);
}

$qLower = mb_strtolower($q);
while (($row = fgetcsv($fh)) !== false) {
    $name = trim((string) ($row[$nameIdx] ?? ''));
    if ($name === '') {
        continue;
    }
    if ($qLower !== '' && mb_strpos(mb_strtolower($name), $qLower) === false) {
        continue;
    }
    $atc = trim((string) ($row[$atcIdx] ?? ''));
    $aware = trim((string) ($row[$awareIdx] ?? ''));
    $extras = [];
    if ($atc !== '') {
        $extras[] = $atc;
    }
    if ($aware !== '') {
        $extras[] = 'AWaRe: ' . $aware;
    }
    $text = $extras ? ($name . ' (' . implode(', ', $extras) . ')') : $name;
    $choices[] = ['value' => $name, 'text' => $text];
    if (count($choices) >= $limit) {
        break;
    }
}
fclose($fh);

$choices[] = ['value' => 'Other antibiotic', 'text' => 'Other antibiotic — specify'];

jsonResponse(['success' => true, 'choices' => $choices]);
