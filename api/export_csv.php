<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

requireAdminOrSupervisor();

$surveyId = (int) ($_GET['survey_id'] ?? 0);
$versionId = (int) ($_GET['version_id'] ?? 0);
$dateFrom = $_GET['date_from'] ?? '';
$dateTo = $_GET['date_to'] ?? '';

$db = getDb();

$sql = "SELECT r.*, s.title AS survey_title, s.survey_code,
               u.full_name AS enumerator_name, u.username AS enumerator_username
        FROM responses r
        JOIN surveys s ON s.id = r.survey_id
        JOIN users u ON u.id = r.enumerator_id
        WHERE r.status = 'completed'";
$params = [];

$teamScope = responseTeamScopeSql('r', 'u');
$sql .= $teamScope['sql'];
$params = array_merge($params, $teamScope['params']);

$surveyScope = managedSurveysSql('s');
$sql .= $surveyScope['sql'];
$params = array_merge($params, $surveyScope['params']);

if ($surveyId > 0) {
    $sql .= ' AND r.survey_id = ?';
    $params[] = $surveyId;
}
if ($versionId > 0) {
    $sql .= ' AND r.survey_version_id = ?';
    $params[] = $versionId;
}
if ($dateFrom !== '') {
    $sql .= ' AND r.submitted_at >= ?';
    $params[] = $dateFrom . ' 00:00:00';
}
if ($dateTo !== '') {
    $sql .= ' AND r.submitted_at <= ?';
    $params[] = $dateTo . ' 23:59:59';
}

$sql .= ' ORDER BY r.submitted_at DESC';
$stmt = $db->prepare($sql);
$stmt->execute($params);
$responses = $stmt->fetchAll();

if (empty($responses)) {
    setFlash('warning', 'No responses to export for the selected filters.');
    redirect('admin/responses.php');
}

$responseIds = array_column($responses, 'id');
$placeholders = implode(',', array_fill(0, count($responseIds), '?'));
$ansStmt = $db->prepare(
    "SELECT response_id, question_name, answer_value FROM answers
     WHERE response_id IN ($placeholders) ORDER BY response_id, question_name"
);
$ansStmt->execute($responseIds);
$answersByResponse = [];
$allQuestions = [];
foreach ($ansStmt->fetchAll() as $row) {
    $answersByResponse[$row['response_id']][$row['question_name']] = $row['answer_value'];
    $allQuestions[$row['question_name']] = true;
}
$questionColumns = array_keys($allQuestions);
sort($questionColumns);

$filename = 'survey_export_' . date('Y-m-d_His') . '.csv';

header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="' . $filename . '"');
header('Pragma: no-cache');
header('Expires: 0');

$out = fopen('php://output', 'w');
// UTF-8 BOM for Excel
fwrite($out, "\xEF\xBB\xBF");

$headers = array_merge(
    [
        'response_id',
        'survey_code',
        'survey_title',
        'survey_version_number',
        'survey_version_id',
        'enumerator_name',
        'enumerator_username',
        'started_at',
        'submitted_at',
        'duration_seconds',
        'latitude',
        'longitude',
        'device_info',
    ],
    $questionColumns
);
fputcsv($out, $headers);

foreach ($responses as $r) {
    $row = [
        $r['id'],
        $r['survey_code'],
        $r['survey_title'],
        $r['survey_version_number'],
        $r['survey_version_id'],
        $r['enumerator_name'],
        $r['enumerator_username'],
        $r['started_at'],
        $r['submitted_at'],
        $r['duration_seconds'],
        $r['latitude'],
        $r['longitude'],
        $r['device_info'],
    ];
    $ans = $answersByResponse[$r['id']] ?? [];
    foreach ($questionColumns as $q) {
        $row[] = $ans[$q] ?? '';
    }
    fputcsv($out, $row);
}

fclose($out);
exit;
