<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

requireAuth();

$surveyId = (int) ($_GET['survey_id'] ?? 0);
if ($surveyId <= 0) {
    jsonResponse(['success' => false, 'message' => 'Invalid survey ID'], 400);
}

$db = getDb();
if (!userCanAccessSurvey($db, $surveyId)) {
    jsonResponse(['success' => false, 'message' => 'You are not assigned to this survey'], 403);
}
$version = getLatestActiveVersion($db, $surveyId);

if (!$version) {
    jsonResponse(['success' => false, 'message' => 'No active version found for this survey'], 404);
}

$definition = json_decode($version['json_definition'], true);
if (json_last_error() !== JSON_ERROR_NONE) {
    jsonResponse(['success' => false, 'message' => 'Corrupt survey JSON in database'], 500);
}

// Load draft if exists
$draft = null;
$userId = currentUserId();
$draftStmt = $db->prepare(
    'SELECT draft_json, updated_at FROM drafts
     WHERE user_id = ? AND survey_id = ? AND survey_version_id = ?'
);
$draftStmt->execute([$userId, $surveyId, $version['id']]);
$draftRow = $draftStmt->fetch();
if ($draftRow) {
    $draft = json_decode($draftRow['draft_json'], true);
}

jsonResponse([
    'success' => true,
    'survey' => [
        'id'          => (int) $version['survey_id'],
        'survey_code' => $version['survey_code'],
        'title'       => $version['title'],
    ],
    'version' => [
        'id'              => (int) $version['id'],
        'version_number'  => (int) $version['version_number'],
    ],
    'definition' => $definition,
    'draft'      => $draft,
    'draft_updated_at' => $draftRow['updated_at'] ?? null,
    'csrf_token' => csrfToken(),
]);
