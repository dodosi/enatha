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
$draftData = $input['data'] ?? null;

if ($surveyId <= 0 || $versionId <= 0 || !is_array($draftData)) {
    jsonResponse(['success' => false, 'message' => 'Missing survey_id, survey_version_id, or data'], 400);
}

$db = getDb();

// Verify version belongs to survey and is active
$stmt = $db->prepare(
    'SELECT id FROM survey_versions WHERE id = ? AND survey_id = ? AND status = ?'
);
$stmt->execute([$versionId, $surveyId, 'active']);
if (!$stmt->fetch()) {
    jsonResponse(['success' => false, 'message' => 'Invalid or inactive survey version'], 400);
}

$draftJson = json_encode($draftData, JSON_UNESCAPED_UNICODE);
$userId = currentUserId();

$upsert = $db->prepare(
    'INSERT INTO drafts (user_id, survey_id, survey_version_id, draft_json, updated_at)
     VALUES (?, ?, ?, ?, NOW())
     ON DUPLICATE KEY UPDATE draft_json = VALUES(draft_json), survey_version_id = VALUES(survey_version_id), updated_at = NOW()'
);
$upsert->execute([$userId, $surveyId, $versionId, $draftJson]);

jsonResponse(['success' => true, 'message' => 'Draft saved', 'saved_at' => date('Y-m-d H:i:s')]);
