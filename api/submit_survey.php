<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

requireAuth();
requireCsrf();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonResponse(['success' => false, 'message' => 'Method not allowed'], 405);
}

$input = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) {
    jsonResponse(['success' => false, 'message' => 'Invalid JSON body'], 400);
}

$surveyId = (int) ($input['survey_id'] ?? 0);
$versionId = (int) ($input['survey_version_id'] ?? 0);
$versionNumber = (int) ($input['survey_version_number'] ?? 0);
$answersData = $input['data'] ?? null;
$startedAt = $input['started_at'] ?? null;
$latitude = isset($input['latitude']) ? (float) $input['latitude'] : null;
$longitude = isset($input['longitude']) ? (float) $input['longitude'] : null;
$deviceInfo = substr((string) ($input['device_info'] ?? ''), 0, 500);

if ($surveyId <= 0 || $versionId <= 0 || $versionNumber <= 0 || !is_array($answersData)) {
    jsonResponse(['success' => false, 'message' => 'Invalid submission data'], 400);
}

$db = getDb();

if (!userCanAccessSurvey($db, $surveyId)) {
    jsonResponse(['success' => false, 'message' => 'You are not assigned to this survey'], 403);
}

$stmt = $db->prepare(
    'SELECT id, version_number, status FROM survey_versions
     WHERE id = ? AND survey_id = ?'
);
$stmt->execute([$versionId, $surveyId]);
$version = $stmt->fetch();

if (!$version) {
    jsonResponse(['success' => false, 'message' => 'Survey version not found'], 404);
}

// Allow submission on inactive version if enumerator started with that version (audit integrity)
if ((int) $version['version_number'] !== $versionNumber) {
    jsonResponse(['success' => false, 'message' => 'Version mismatch'], 400);
}

$submittedAt = date('Y-m-d H:i:s');
$durationSeconds = null;

if ($startedAt) {
    $startTs = strtotime($startedAt);
    if ($startTs) {
        $durationSeconds = max(0, time() - $startTs);
    }
}

try {
    $db->beginTransaction();

    $respIns = $db->prepare(
        'INSERT INTO responses (
            survey_id, survey_version_id, survey_version_number, enumerator_id,
            started_at, submitted_at, duration_seconds, status,
            latitude, longitude, device_info
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    $respIns->execute([
        $surveyId,
        $versionId,
        $versionNumber,
        currentUserId(),
        $startedAt ? date('Y-m-d H:i:s', strtotime($startedAt)) : null,
        $submittedAt,
        $durationSeconds,
        'completed',
        $latitude,
        $longitude,
        $deviceInfo ?: null,
    ]);
    $responseId = (int) $db->lastInsertId();

    $flatAnswers = flattenSurveyAnswers($answersData);
    $ansIns = $db->prepare(
        'INSERT INTO answers (response_id, question_name, question_type, answer_value) VALUES (?, ?, ?, ?)'
    );
    foreach ($flatAnswers as $ans) {
        $ansIns->execute([
            $responseId,
            substr($ans['question_name'], 0, 255),
            substr($ans['question_type'], 0, 50),
            $ans['answer_value'],
        ]);
    }

    // Clear draft after successful submit
    $delDraft = $db->prepare('DELETE FROM drafts WHERE user_id = ? AND survey_id = ?');
    $delDraft->execute([currentUserId(), $surveyId]);

    $db->commit();

    jsonResponse([
        'success'     => true,
        'message'     => 'Survey submitted successfully',
        'response_id' => $responseId,
        'redirect'    => url('surveys/select_survey.php'),
    ]);
} catch (Exception $e) {
    $db->rollBack();
    jsonResponse(['success' => false, 'message' => 'Submission failed. Please try again.'], 500);
}
