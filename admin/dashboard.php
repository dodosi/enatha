<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdminOrSupervisor();

$db = getDb();

$stats = [
    'surveys'    => (int) $db->query('SELECT COUNT(*) FROM surveys')->fetchColumn(),
    'versions'   => (int) $db->query('SELECT COUNT(*) FROM survey_versions')->fetchColumn(),
    'responses'  => (int) $db->query("SELECT COUNT(*) FROM responses WHERE status = 'completed'")->fetchColumn(),
    'users'      => (int) $db->query("SELECT COUNT(*) FROM users WHERE status = 'active'")->fetchColumn(),
    'enumerators'=> (int) $db->query("SELECT COUNT(*) FROM users WHERE role = 'enumerator' AND status = 'active'")->fetchColumn(),
];

$recent = $db->query(
    "SELECT r.id, r.submitted_at, s.title, sv.version_number, u.full_name AS enumerator
     FROM responses r
     JOIN surveys s ON s.id = r.survey_id
     JOIN survey_versions sv ON sv.id = r.survey_version_id
     JOIN users u ON u.id = r.enumerator_id
     WHERE r.status = 'completed'
     ORDER BY r.submitted_at DESC
     LIMIT 10"
)->fetchAll();

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
    <?php if (hasRole('admin')): ?>
    <a href="<?= e(url('admin/upload_survey.php')) ?>" class="btn btn-primary">Upload Survey JSON</a>
    <a href="<?= e(url('admin/users.php')) ?>" class="btn btn-outline-primary">Manage Users</a>
    <a href="<?= e(url('admin/register_user.php')) ?>" class="btn btn-outline-primary">Register User</a>
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
