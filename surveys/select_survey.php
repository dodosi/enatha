<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAuth();

if (!canTakeSurveys()) {
    setFlash('danger', 'You do not have permission to take surveys.');
    redirect('index.php');
}

$db = getDb();
$scope = surveyScopeSql('s');

$sql = "SELECT s.id, s.survey_code, s.title, s.description,
            sv.id AS version_id, sv.version_number
     FROM surveys s
     INNER JOIN survey_versions sv ON sv.survey_id = s.id AND sv.status = 'active'
     INNER JOIN (
         SELECT survey_id, MAX(version_number) AS max_ver
         FROM survey_versions WHERE status = 'active'
         GROUP BY survey_id
     ) latest ON latest.survey_id = s.id AND sv.version_number = latest.max_ver
     WHERE 1=1" . $scope['sql'] . '
     ORDER BY s.title';
$stmt = $db->prepare($sql);
$stmt->execute($scope['params']);
$available = $stmt->fetchAll();

$pageTitle = 'Select Survey';
require dirname(__DIR__) . '/includes/layout_header.php';
$flash = getFlash();
?>
<?php if ($flash): ?>
<div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
<?php endif; ?>

<h1 class="h3 mb-4">Select Survey</h1>

<?php if (empty($available)): ?>
<div class="alert alert-warning">
    No surveys are available for your account. Contact your leader or administrator.
</div>
<?php else: ?>
<div class="row g-3">
    <?php foreach ($available as $survey): ?>
    <div class="col-12 col-md-6 col-lg-4">
        <div class="card card-survey h-100">
            <div class="card-body d-flex flex-column">
                <h2 class="h5 card-title"><?= e($survey['title']) ?></h2>
                <p class="text-muted small mb-2"><?= e($survey['survey_code']) ?> · Version <?= (int) $survey['version_number'] ?></p>
                <?php if (!empty($survey['description'])): ?>
                <p class="card-text small flex-grow-1"><?= e($survey['description']) ?></p>
                <?php endif; ?>
                <div class="d-flex gap-2 mt-auto">
                    <a href="<?= e(url('surveys/take_survey.php?survey_id=' . (int) $survey['id'])) ?>"
                       class="btn btn-primary flex-grow-1">Start Survey</a>
                    <a href="<?= e(url('surveys/print_survey.php?survey_id=' . (int) $survey['id'])) ?>"
                       class="btn btn-outline-secondary" target="_blank" rel="noopener">Printable form</a>
                </div>
            </div>
        </div>
    </div>
    <?php endforeach; ?>
</div>
<?php endif; ?>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
