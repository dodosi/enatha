<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdminOrSupervisor();

$db = getDb();

$surveyId = (int) ($_GET['survey_id'] ?? 0);
$versionId = (int) ($_GET['version_id'] ?? 0);
$dateFrom = $_GET['date_from'] ?? '';
$dateTo = $_GET['date_to'] ?? '';

$surveyScope = managedSurveysSql('s');
$sStmt = $db->prepare(
    'SELECT s.id, s.survey_code, s.title FROM surveys s WHERE 1=1' . $surveyScope['sql'] . ' ORDER BY s.title'
);
$sStmt->execute($surveyScope['params']);
$surveys = $sStmt->fetchAll();

$versions = [];
if ($surveyId > 0) {
    $vStmt = $db->prepare('SELECT id, version_number, status FROM survey_versions WHERE survey_id = ? ORDER BY version_number DESC');
    $vStmt->execute([$surveyId]);
    $versions = $vStmt->fetchAll();
}

$sql = "SELECT r.id, r.submitted_at, r.survey_version_number, r.duration_seconds,
               r.latitude, r.longitude, r.status,
               s.title AS survey_title, s.survey_code,
               u.full_name AS enumerator
        FROM responses r
        JOIN surveys s ON s.id = r.survey_id
        JOIN users u ON u.id = r.enumerator_id
        WHERE 1=1";
$params = [];

$teamScope = responseTeamScopeSql('r', 'u');
$sql .= $teamScope['sql'];
$params = array_merge($params, $teamScope['params']);

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

$sql .= " ORDER BY r.submitted_at DESC LIMIT 500";
$stmt = $db->prepare($sql);
$stmt->execute($params);
$responses = $stmt->fetchAll();

$exportQuery = http_build_query(array_filter([
    'survey_id'  => $surveyId ?: null,
    'version_id' => $versionId ?: null,
    'date_from'  => $dateFrom ?: null,
    'date_to'    => $dateTo ?: null,
]));

$pageTitle = 'Responses';
require dirname(__DIR__) . '/includes/layout_header.php';
$flash = getFlash();
?>
<?php if ($flash): ?>
<div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
<?php endif; ?>

<h1 class="h3 mb-4">Responses</h1>

<div class="card card-survey mb-4">
    <div class="card-body">
        <form method="get" class="row g-3 align-items-end">
            <div class="col-md-3">
                <label class="form-label">Survey</label>
                <select name="survey_id" class="form-select" onchange="this.form.submit()">
                    <option value="">All surveys</option>
                    <?php foreach ($surveys as $s): ?>
                    <option value="<?= (int) $s['id'] ?>" <?= $surveyId === (int) $s['id'] ? 'selected' : '' ?>>
                        <?= e($s['title']) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Version</label>
                <select name="version_id" class="form-select">
                    <option value="">All versions</option>
                    <?php foreach ($versions as $v): ?>
                    <option value="<?= (int) $v['id'] ?>" <?= $versionId === (int) $v['id'] ? 'selected' : '' ?>>
                        v<?= (int) $v['version_number'] ?> (<?= e($v['status']) ?>)
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">From</label>
                <input type="date" name="date_from" class="form-control" value="<?= e($dateFrom) ?>">
            </div>
            <div class="col-md-2">
                <label class="form-label">To</label>
                <input type="date" name="date_to" class="form-control" value="<?= e($dateTo) ?>">
            </div>
            <div class="col-md-3">
                <button type="submit" class="btn btn-primary">Filter</button>
                <?php if (!empty($responses)): ?>
                <a href="<?= e(url('api/export_csv.php?' . $exportQuery)) ?>" class="btn btn-success">Export CSV</a>
                <?php endif; ?>
            </div>
        </form>
    </div>
</div>

<div class="card card-survey">
    <div class="table-responsive">
        <table class="table table-hover mb-0">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Survey</th>
                    <th>Ver.</th>
                    <th>Enumerator</th>
                    <th>Submitted</th>
                    <th>Duration</th>
                    <th>Status</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($responses)): ?>
                <tr><td colspan="8" class="text-center text-muted py-4">No responses match your filters.</td></tr>
                <?php else: ?>
                <?php foreach ($responses as $r): ?>
                <tr>
                    <td>
                        <a href="<?= e(url('admin/view_response.php?id=' . (int) $r['id'])) ?>">
                            <?= (int) $r['id'] ?>
                        </a>
                    </td>
                    <td>
                        <a href="<?= e(url('admin/view_response.php?id=' . (int) $r['id'])) ?>" class="text-decoration-none text-body">
                            <?= e($r['survey_title']) ?>
                        </a>
                    </td>
                    <td>v<?= (int) $r['survey_version_number'] ?></td>
                    <td><?= e($r['enumerator']) ?></td>
                    <td><?= e($r['submitted_at'] ?? '-') ?></td>
                    <td><?= $r['duration_seconds'] !== null ? (int) $r['duration_seconds'] . 's' : '-' ?></td>
                    <td><span class="badge bg-success"><?= e($r['status']) ?></span></td>
                    <td class="small">
                        <a href="<?= e(url('admin/view_response.php?id=' . (int) $r['id'])) ?>">View answers</a>
                    </td>
                </tr>
                <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
    <?php if (count($responses) >= 500): ?>
    <div class="card-footer text-muted small">Showing latest 500 records. Use date filters or export for full data.</div>
    <?php endif; ?>
</div>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
