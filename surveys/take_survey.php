<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAuth();

if (!canTakeSurveys()) {
    setFlash('danger', 'You do not have permission to take surveys.');
    redirect('index.php');
}

$surveyId = (int) ($_GET['survey_id'] ?? 0);
if ($surveyId <= 0) {
    setFlash('danger', 'Invalid survey.');
    redirect('surveys/select_survey.php');
}

$db = getDb();
if (!userCanAccessSurvey($db, $surveyId)) {
    setFlash('danger', 'You are not assigned to this survey.');
    redirect('surveys/select_survey.php');
}
$version = getLatestActiveVersion($db, $surveyId);
if (!$version) {
    setFlash('danger', 'This survey has no active version.');
    redirect('surveys/select_survey.php');
}

$pageTitle = $version['title'];
require dirname(__DIR__) . '/includes/layout_header.php';
?>
<div class="mb-3 d-flex justify-content-between align-items-center flex-wrap gap-2">
    <div>
        <a href="<?= e(url('surveys/select_survey.php')) ?>" class="btn btn-outline-secondary btn-sm">&larr; Back</a>
        <h1 class="h5 d-inline ms-2 mb-0" id="surveyTitle"><?= e($version['title']) ?></h1>
    </div>
    <span class="autosave-status" id="autosaveStatus"></span>
</div>

<div id="surveyLoading" class="text-center py-5">
    <div class="spinner-border text-primary" role="status"></div>
    <p class="mt-2 text-muted">Loading questionnaire...</p>
</div>

<div id="surveyError" class="alert alert-danger d-none"></div>

<div class="survey-container card card-survey d-none" id="surveyContainer">
    <div id="surveyElement"></div>
</div>

<link href="https://unpkg.com/survey-core@1.11.10/defaultV2.min.css" rel="stylesheet">
<script src="https://unpkg.com/survey-core@1.11.10/survey.core.min.js"></script>
<script src="https://unpkg.com/survey-js-ui@1.11.10/survey-js-ui.min.js"></script>

<script>
window.SURVEY_CONFIG = {
    surveyId: <?= (int) $surveyId ?>,
    csrfToken: <?= json_encode(csrfToken()) ?>,
    baseUrl: <?= json_encode(rtrim(BASE_URL, '/')) ?>,
    autosaveInterval: <?= (int) AUTOSAVE_INTERVAL ?>
};
</script>
<script>
document.addEventListener('DOMContentLoaded', function () {
    var obs = new MutationObserver(function () {
        var el = document.getElementById('surveyElement');
        if (el && el.children.length > 0) {
            document.getElementById('surveyContainer').classList.remove('d-none');
        }
    });
    var target = document.getElementById('surveyElement');
    if (target) obs.observe(target, { childList: true });
});
</script>
<script src="<?= e(url('assets/js/survey-app.js')) ?>?v=<?= (int) @filemtime(dirname(__DIR__) . '/assets/js/survey-app.js') ?>"></script>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
