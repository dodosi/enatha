<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdminOrSupervisor();

$db = getDb();
$teamScope = responseTeamScopeSql('r', 'u');
$surveyScope = managedSurveysSql('s');

$surveyCountSql = 'SELECT COUNT(*) FROM surveys s WHERE 1=1' . $surveyScope['sql'];
$surveyCountStmt = $db->prepare($surveyCountSql);
$surveyCountStmt->execute($surveyScope['params']);

$versionCountSql = 'SELECT COUNT(*) FROM survey_versions sv
    JOIN surveys s ON s.id = sv.survey_id WHERE 1=1' . $surveyScope['sql'];
$versionCountStmt = $db->prepare($versionCountSql);
$versionCountStmt->execute($surveyScope['params']);

$responseCountSql = "SELECT COUNT(*) FROM responses r
    JOIN users u ON u.id = r.enumerator_id
    JOIN surveys s ON s.id = r.survey_id
    WHERE r.status = 'completed'" . $teamScope['sql'] . $surveyScope['sql'];
$responseCountStmt = $db->prepare($responseCountSql);
$responseCountStmt->execute(array_merge($teamScope['params'], $surveyScope['params']));

if (isSuperAdmin()) {
    $userCount = (int) $db->query("SELECT COUNT(*) FROM users WHERE status = 'active'")->fetchColumn();
    $enumCount = (int) $db->query("SELECT COUNT(*) FROM users WHERE role = 'enumerator' AND status = 'active'")->fetchColumn();
} else {
    $leaderId = teamLeaderId();
    $uStmt = $db->prepare("SELECT COUNT(*) FROM users WHERE status = 'active' AND (id = ? OR leader_id = ?)");
    $uStmt->execute([$leaderId, $leaderId]);
    $userCount = (int) $uStmt->fetchColumn();
    $eStmt = $db->prepare("SELECT COUNT(*) FROM users WHERE role = 'enumerator' AND status = 'active' AND leader_id = ?");
    $eStmt->execute([$leaderId]);
    $enumCount = (int) $eStmt->fetchColumn();
}

$stats = [
    'surveys'     => (int) $surveyCountStmt->fetchColumn(),
    'versions'    => (int) $versionCountStmt->fetchColumn(),
    'responses'   => (int) $responseCountStmt->fetchColumn(),
    'users'       => $userCount,
    'enumerators' => $enumCount,
];

$recentSql = "SELECT r.id, r.submitted_at, s.title, sv.version_number, u.full_name AS enumerator
     FROM responses r
     JOIN surveys s ON s.id = r.survey_id
     JOIN survey_versions sv ON sv.id = r.survey_version_id
     JOIN users u ON u.id = r.enumerator_id
     WHERE r.status = 'completed'" . $teamScope['sql'] . $surveyScope['sql'] . '
     ORDER BY r.submitted_at DESC
     LIMIT 10';
$recentStmt = $db->prepare($recentSql);
$recentStmt->execute(array_merge($teamScope['params'], $surveyScope['params']));
$recent = $recentStmt->fetchAll();

$pageTitle = 'Dashboard';
require dirname(__DIR__) . '/includes/layout_header.php';
$flash = getFlash();
?>
<?php if ($flash): ?>
<div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
<?php endif; ?>

<h1 class="h3 mb-4">Dashboard</h1>

<div class="row g-3 mb-4">
    <div class="col-6 col-md-4 col-lg">
        <div class="card card-survey h-100">
            <div class="card-body">
                <div class="text-muted small">Surveys</div>
                <div class="h3 mb-0"><?= (int) $stats['surveys'] ?></div>
            </div>
        </div>
    </div>
    <div class="col-6 col-md-4 col-lg">
        <div class="card card-survey h-100">
            <div class="card-body">
                <div class="text-muted small">Versions</div>
                <div class="h3 mb-0"><?= (int) $stats['versions'] ?></div>
            </div>
        </div>
    </div>
    <div class="col-6 col-md-4 col-lg">
        <div class="card card-survey h-100">
            <div class="card-body">
                <div class="text-muted small">Completed Responses</div>
                <div class="h3 mb-0"><?= (int) $stats['responses'] ?></div>
            </div>
        </div>
    </div>
    <div class="col-6 col-md-4 col-lg">
        <div class="card card-survey h-100">
            <div class="card-body">
                <div class="text-muted small">Active Users</div>
                <div class="h3 mb-0"><?= (int) $stats['users'] ?></div>
            </div>
        </div>
    </div>
    <div class="col-6 col-md-4 col-lg">
        <div class="card card-survey h-100">
            <div class="card-body">
                <div class="text-muted small">Enumerators</div>
                <div class="h3 mb-0"><?= (int) $stats['enumerators'] ?></div>
            </div>
        </div>
    </div>
</div>

<div class="d-flex flex-wrap gap-2 mb-4">
    <?php if (canManageSurveyCatalog()): ?>
    <a href="<?= e(url('admin/upload_survey.php')) ?>" class="btn btn-primary">Upload Survey JSON</a>
    <?php endif; ?>
    <?php if (canManageTeam()): ?>
    <a href="<?= e(url('admin/users.php')) ?>" class="btn btn-outline-primary">Manage Users</a>
    <a href="<?= e(url('admin/register_user.php')) ?>" class="btn btn-outline-primary">Register User</a>
    <a href="<?= e(url('admin/assign_surveys.php')) ?>" class="btn btn-outline-primary">Assign Surveys</a>
    <?php endif; ?>
    <a href="<?= e(url('admin/surveys.php')) ?>" class="btn btn-outline-secondary">View Surveys</a>
    <a href="<?= e(url('admin/responses.php')) ?>" class="btn btn-outline-secondary">View Responses</a>
</div>

<div class="card card-survey">
    <div class="card-header bg-white"><strong>Recent Submissions</strong></div>
    <div class="table-responsive">
        <table class="table table-hover mb-0">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Survey</th>
                    <th>Version</th>
                    <th>Enumerator</th>
                    <th>Submitted</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($recent)): ?>
                <tr><td colspan="5" class="text-muted text-center py-4">No submissions yet.</td></tr>
                <?php else: ?>
                <?php foreach ($recent as $row): ?>
                <tr>
                    <td><?= (int) $row['id'] ?></td>
                    <td><?= e($row['title']) ?></td>
                    <td>v<?= (int) $row['version_number'] ?></td>
                    <td><?= e($row['enumerator']) ?></td>
                    <td><?= e($row['submitted_at'] ?? '-') ?></td>
                </tr>
                <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
