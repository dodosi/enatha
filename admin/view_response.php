<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdminOrSupervisor();

$db = getDb();
$responseId = (int) ($_GET['id'] ?? 0);

if ($responseId <= 0) {
    setFlash('danger', 'Response not found.');
    redirect('admin/responses.php');
}

$sql = "SELECT r.id, r.survey_id, r.survey_version_id, r.survey_version_number,
               r.started_at, r.submitted_at, r.duration_seconds, r.status,
               r.latitude, r.longitude, r.device_info, r.created_at,
               s.title AS survey_title, s.survey_code,
               u.full_name AS enumerator, u.username AS enumerator_username,
               sv.json_definition
        FROM responses r
        JOIN surveys s ON s.id = r.survey_id
        JOIN users u ON u.id = r.enumerator_id
        LEFT JOIN survey_versions sv ON sv.id = r.survey_version_id
        WHERE r.id = ?";
$params = [$responseId];

$teamScope = responseTeamScopeSql('r', 'u');
$sql .= $teamScope['sql'];
$params = array_merge($params, $teamScope['params']);

$surveyScope = managedSurveysSql('s');
$sql .= $surveyScope['sql'];
$params = array_merge($params, $surveyScope['params']);

$stmt = $db->prepare($sql);
$stmt->execute($params);
$response = $stmt->fetch();

if (!$response) {
    setFlash('danger', 'Response not found or you do not have access.');
    redirect('admin/responses.php');
}

$aStmt = $db->prepare(
    'SELECT question_name, question_type, answer_value
     FROM answers
     WHERE response_id = ?
     ORDER BY id'
);
$aStmt->execute([$responseId]);
$answers = $aStmt->fetchAll();

$titleMap = surveyQuestionTitleMap((string) ($response['json_definition'] ?? ''));

$pageTitle = 'Response #' . $responseId;
require dirname(__DIR__) . '/includes/layout_header.php';
$flash = getFlash();
?>
<?php if ($flash): ?>
<div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
<?php endif; ?>

<div class="d-flex justify-content-between align-items-start mb-4 flex-wrap gap-2">
    <div>
        <h1 class="h3 mb-1">Response #<?= (int) $response['id'] ?></h1>
        <p class="text-muted mb-0"><?= e($response['survey_title']) ?></p>
    </div>
    <a href="<?= e(url('admin/responses.php')) ?>" class="btn btn-outline-secondary">Back to Responses</a>
</div>

<div class="card card-survey mb-4">
    <div class="card-header bg-white"><strong>Submission details</strong></div>
    <div class="card-body">
        <div class="row g-3 small">
            <div class="col-md-4">
                <div class="text-muted">Survey code</div>
                <div><?= e($response['survey_code']) ?></div>
            </div>
            <div class="col-md-4">
                <div class="text-muted">Version</div>
                <div>v<?= (int) $response['survey_version_number'] ?></div>
            </div>
            <div class="col-md-4">
                <div class="text-muted">Status</div>
                <div><span class="badge bg-success"><?= e($response['status']) ?></span></div>
            </div>
            <div class="col-md-4">
                <div class="text-muted">Enumerator</div>
                <div><?= e($response['enumerator']) ?> <span class="text-muted">(<?= e($response['enumerator_username']) ?>)</span></div>
            </div>
            <div class="col-md-4">
                <div class="text-muted">Submitted</div>
                <div><?= e($response['submitted_at'] ?? '—') ?></div>
            </div>
            <div class="col-md-4">
                <div class="text-muted">Duration</div>
                <div><?= $response['duration_seconds'] !== null ? (int) $response['duration_seconds'] . 's' : '—' ?></div>
            </div>
            <?php if ($response['latitude'] !== null && $response['longitude'] !== null): ?>
            <div class="col-md-4">
                <div class="text-muted">Location</div>
                <div><?= e($response['latitude']) ?>, <?= e($response['longitude']) ?></div>
            </div>
            <?php endif; ?>
            <?php if (!empty($response['device_info'])): ?>
            <div class="col-md-8">
                <div class="text-muted">Device</div>
                <div class="text-break"><?= e($response['device_info']) ?></div>
            </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<div class="card card-survey">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <strong>Answers</strong>
        <span class="text-muted small"><?= count($answers) ?> field<?= count($answers) === 1 ? '' : 's' ?></span>
    </div>
    <?php if (empty($answers)): ?>
    <div class="card-body text-muted">No answers stored for this response.</div>
    <?php else: ?>
    <div class="table-responsive">
        <table class="table table-hover mb-0">
            <thead>
                <tr>
                    <th style="width:40%">Question</th>
                    <th>Answer</th>
                    <th class="text-muted" style="width:12%">Type</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($answers as $a): ?>
                <?php
                    $label = resolveQuestionLabel($a['question_name'], $titleMap);
                    $display = formatAnswerDisplay($a['answer_value'], $a['question_type']);
                ?>
                <tr>
                    <td>
                        <div><?= e($label) ?></div>
                        <?php if ($label !== $a['question_name']): ?>
                        <div class="text-muted small font-monospace"><?= e($a['question_name']) ?></div>
                        <?php endif; ?>
                    </td>
                    <td class="text-break" style="white-space: pre-wrap;"><?= e($display) ?></td>
                    <td class="text-muted small"><?= e($a['question_type']) ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <?php endif; ?>
</div>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
