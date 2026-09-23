<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdminOrSupervisor();

$db = getDb();

// Toggle version status (admin only)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && hasRole('admin')) {
    if (!validateCsrf()) {
        setFlash('danger', 'Invalid security token.');
        redirect('admin/surveys.php');
    }
    $action = $_POST['action'] ?? '';
    $versionId = (int) ($_POST['version_id'] ?? 0);

    if ($action === 'activate' && $versionId > 0) {
        $stmt = $db->prepare('SELECT survey_id FROM survey_versions WHERE id = ?');
        $stmt->execute([$versionId]);
        $ver = $stmt->fetch();
        if ($ver) {
            $db->prepare('UPDATE survey_versions SET status = ? WHERE survey_id = ?')
                ->execute(['inactive', $ver['survey_id']]);
            $db->prepare('UPDATE survey_versions SET status = ? WHERE id = ?')
                ->execute(['active', $versionId]);
            setFlash('success', 'Version activated. New submissions will use this version.');
        }
    } elseif ($action === 'deactivate' && $versionId > 0) {
        $db->prepare('UPDATE survey_versions SET status = ? WHERE id = ?')
            ->execute(['inactive', $versionId]);
        setFlash('success', 'Version deactivated.');
    }
    redirect('admin/surveys.php');
}

$surveys = $db->query(
    'SELECT s.*,
            (SELECT COUNT(*) FROM survey_versions sv WHERE sv.survey_id = s.id) AS version_count,
            (SELECT MAX(sv.version_number) FROM survey_versions sv WHERE sv.survey_id = s.id) AS latest_version
     FROM surveys s ORDER BY s.title'
)->fetchAll();

$versionsBySurvey = [];
if (!empty($surveys)) {
    $ids = array_column($surveys, 'id');
    $placeholders = implode(',', array_fill(0, count($ids), '?'));
    $stmt = $db->prepare(
        "SELECT sv.*, u.full_name AS created_by_name
         FROM survey_versions sv
         LEFT JOIN users u ON u.id = sv.created_by
         WHERE sv.survey_id IN ($placeholders)
         ORDER BY sv.survey_id, sv.version_number DESC"
    );
    $stmt->execute($ids);
    foreach ($stmt->fetchAll() as $v) {
        $versionsBySurvey[$v['survey_id']][] = $v;
    }
}

$pageTitle = 'Surveys';
require dirname(__DIR__) . '/includes/layout_header.php';
$flash = getFlash();
?>
<?php if ($flash): ?>
<div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
<?php endif; ?>

<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <h1 class="h3 mb-0">Surveys</h1>
    <?php if (hasRole('admin')): ?>
    <a href="<?= e(url('admin/upload_survey.php')) ?>" class="btn btn-primary btn-sm">Upload New Version</a>
    <?php endif; ?>
</div>

<?php foreach ($surveys as $survey): ?>
<div class="card card-survey mb-4">
    <div class="card-header bg-white d-flex justify-content-between flex-wrap gap-2">
        <div>
            <strong><?= e($survey['title']) ?></strong>
            <span class="badge bg-secondary ms-1"><?= e($survey['survey_code']) ?></span>
        </div>
        <span class="text-muted small">
            <?= (int) $survey['version_count'] ?> version(s)
            <?php if ($survey['latest_version']): ?> · latest v<?= (int) $survey['latest_version'] ?><?php endif; ?>
        </span>
    </div>
    <?php if (!empty($survey['description'])): ?>
    <div class="card-body py-2 border-bottom">
        <p class="small text-muted mb-0"><?= e($survey['description']) ?></p>
    </div>
    <?php endif; ?>
    <div class="table-responsive">
        <table class="table table-sm mb-0">
            <thead>
                <tr>
                    <th>Version</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>By</th>
                    <?php if (hasRole('admin')): ?><th>Actions</th><?php endif; ?>
                </tr>
            </thead>
            <tbody>
                <?php
                $versions = $versionsBySurvey[$survey['id']] ?? [];
                if (empty($versions)):
                ?>
                <tr><td colspan="5" class="text-muted">No versions uploaded.</td></tr>
                <?php else: ?>
                <?php foreach ($versions as $v): ?>
                <tr>
                    <td>v<?= (int) $v['version_number'] ?></td>
                    <td>
                        <?php if ($v['status'] === 'active'): ?>
                        <span class="badge bg-success">Active</span>
                        <?php else: ?>
                        <span class="badge bg-secondary">Inactive</span>
                        <?php endif; ?>
                    </td>
                    <td><?= e($v['created_at']) ?></td>
                    <td><?= e($v['created_by_name'] ?? '-') ?></td>
                    <?php if (hasRole('admin')): ?>
                    <td>
                        <form method="post" class="d-inline">
                            <?= csrfField() ?>
                            <input type="hidden" name="version_id" value="<?= (int) $v['id'] ?>">
                            <?php if ($v['status'] !== 'active'): ?>
                            <button type="submit" name="action" value="activate" class="btn btn-link btn-sm p-0">Activate</button>
                            <?php else: ?>
                            <button type="submit" name="action" value="deactivate" class="btn btn-link btn-sm p-0 text-danger"
                                    onclick="return confirm('Deactivate this version? Enumerators cannot use it until another is active.');">Deactivate</button>
                            <?php endif; ?>
                        </form>
                    </td>
                    <?php endif; ?>
                </tr>
                <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>
<?php endforeach; ?>

<?php if (empty($surveys)): ?>
<div class="alert alert-info">No surveys yet. Upload your first SurveyJS JSON.</div>
<?php endif; ?>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
