<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
require_once dirname(__DIR__) . '/includes/survey_print.php';
requireAuth();

if (!canTakeSurveys() && !canViewAdminDashboard()) {
    setFlash('danger', 'You do not have permission to view survey forms.');
    redirect('index.php');
}

$surveyId = (int) ($_GET['survey_id'] ?? 0);
$versionId = (int) ($_GET['version_id'] ?? 0);
$db = getDb();

$version = null;
if ($versionId > 0 && canViewAdminDashboard()) {
    $stmt = $db->prepare(
        'SELECT sv.*, s.title, s.survey_code, s.owner_id
         FROM survey_versions sv
         JOIN surveys s ON s.id = sv.survey_id
         WHERE sv.id = ?'
    );
    $stmt->execute([$versionId]);
    $version = $stmt->fetch() ?: null;
} elseif ($surveyId > 0) {
    $version = getLatestActiveVersion($db, $surveyId);
    if ($version && !isset($version['owner_id'])) {
        $o = $db->prepare('SELECT owner_id FROM surveys WHERE id = ?');
        $o->execute([(int) $version['survey_id']]);
        $version['owner_id'] = $o->fetchColumn();
    }
}

if ($version) {
    $sid = (int) $version['survey_id'];
    $allowed = isSuperAdmin()
        || (isLeader() && (int) ($version['owner_id'] ?? 0) === currentUserId())
        || userCanAccessSurvey($db, $sid);
    if (!$allowed) {
        $version = null;
    }
}

if (!$version) {
    setFlash('danger', 'No printable version found for this survey.');
    redirect(canViewAdminDashboard() ? 'admin/surveys.php' : 'surveys/select_survey.php');
}

$definition = json_decode($version['json_definition'], true);
if (!is_array($definition)) {
    setFlash('danger', 'The survey JSON for this version could not be read.');
    redirect(canViewAdminDashboard() ? 'admin/surveys.php' : 'surveys/select_survey.php');
}

$formTitle = trim((string) (is_array($definition['title'] ?? null)
    ? ($definition['title']['default'] ?? reset($definition['title']))
    : ($definition['title'] ?? ''))) ?: $version['title'];
$formDescription = trim((string) (is_array($definition['description'] ?? null)
    ? ($definition['description']['default'] ?? reset($definition['description']))
    : ($definition['description'] ?? '')));
$versionLabel = $version['survey_code'] . ' · Version ' . (int) $version['version_number'];

$renderer = new SurveyPrintRenderer($definition);
$formHtml = $renderer->render();

// @page margin boxes take literal CSS strings, not HTML
$cssFooter = addcslashes(str_replace(['<', '>', "\n", "\r"], ' ', $versionLabel), "\"\\");
$backUrl = canViewAdminDashboard() ? url('admin/surveys.php') : url('surveys/select_survey.php');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= e($formTitle) ?> (printable) - <?= e(APP_NAME) ?></title>
    <style>
        @page {
            size: A4;
            margin: 14mm 12mm 16mm 12mm;
            @bottom-left { content: "<?= $cssFooter ?>"; font-size: 8pt; color: #555; }
            @bottom-right { content: "Page " counter(page) " of " counter(pages); font-size: 8pt; color: #555; }
        }
        * { box-sizing: border-box; }
        body { font-family: Arial, Helvetica, sans-serif; font-size: 10.5pt; color: #111; margin: 0; background: #eef1f4; }
        .sp-toolbar { position: sticky; top: 0; z-index: 10; background: #1f3b57; color: #fff; padding: 10px 16px;
            display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
        .sp-toolbar a, .sp-toolbar button { font: inherit; font-size: 10pt; padding: 6px 14px; border-radius: 4px;
            border: 1px solid #fff; background: transparent; color: #fff; text-decoration: none; cursor: pointer; }
        .sp-toolbar button.primary { background: #fff; color: #1f3b57; font-weight: bold; }
        .sp-toolbar span { font-size: 9pt; opacity: .85; }
        .sp-sheet { max-width: 210mm; margin: 16px auto; background: #fff; padding: 14mm 12mm; box-shadow: 0 1px 6px rgba(0,0,0,.15); }
        .sp-form-head { border-bottom: 2px solid #111; padding-bottom: 6px; margin-bottom: 10px; }
        .sp-form-head h1 { font-size: 15pt; margin: 0 0 4px; }
        .sp-form-head .sp-version { font-size: 9pt; color: #444; }
        .sp-form-head p { font-size: 9.5pt; margin: 4px 0 0; color: #333; }
        .sp-admin-box { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 16px; border: 1px solid #111; padding: 8px; margin: 8px 0; font-size: 9.5pt; }
        .sp-admin-box div { display: flex; align-items: flex-end; gap: 6px; }
        .sp-admin-box span.sp-fill { flex: 1; border-bottom: 1px solid #111; height: 16px; }
        .sp-instructions { background: #f4f6f8; border: 1px solid #c9d1d9; padding: 6px 10px; font-size: 9pt; margin-bottom: 10px; }
        .sp-instructions ul { margin: 2px 0 0 16px; padding: 0; }
        .sp-section-title { font-size: 12pt; background: #1f3b57; color: #fff; padding: 4px 8px; margin: 14px 0 6px;
            break-after: avoid; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .sp-section-desc { font-size: 9pt; color: #333; margin: 0 0 6px; }
        .sp-q { padding: 5px 0 7px; border-bottom: 1px dotted #bbb; break-inside: avoid; }
        .sp-q-head { font-weight: bold; }
        .sp-num { display: inline-block; min-width: 38px; color: #1f3b57; }
        .sp-req { color: #b00020; }
        .sp-cond { font-size: 9pt; font-style: italic; color: #7a4b00; margin: 2px 0 2px 38px; }
        .sp-cond-section { margin-left: 0; font-weight: bold; }
        .sp-desc, .sp-hint { font-size: 8.8pt; color: #555; margin: 2px 0 2px 38px; }
        .sp-hint { font-style: italic; }
        .sp-note { font-size: 9.5pt; background: #fafafa; border-left: 3px solid #1f3b57; padding: 4px 8px; margin: 6px 0; }
        .sp-choices { list-style: none; margin: 3px 0 0 38px; padding: 0; }
        .sp-choices.sp-cols { columns: 2; column-gap: 20px; }
        .sp-choices li { margin: 2px 0; break-inside: avoid; display: flex; align-items: flex-start; gap: 6px; }
        .sp-box { display: inline-block; flex: 0 0 auto; width: 11px; height: 11px; border: 1px solid #111; margin-top: 2px; }
        .sp-rank-box { display: inline-block; flex: 0 0 auto; width: 22px; height: 14px; border: 1px solid #111; }
        .sp-other { width: 100%; }
        .sp-inline-line { flex: 1; border-bottom: 1px solid #111; min-width: 120px; height: 14px; }
        .sp-line { border-bottom: 1px solid #111; height: 20px; margin-left: 38px; }
        .sp-write-list { margin: 2px 0 0 38px; padding-left: 18px; }
        .sp-write-list .sp-line { margin-left: 0; }
        .sp-short-line { display: inline-block; border-bottom: 1px solid #111; width: 120px; height: 18px; margin-left: 38px; }
        .sp-date { margin: 6px 0 0 38px; letter-spacing: 1px; }
        .sp-rating { margin: 3px 0 0 38px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .sp-rate { display: inline-block; min-width: 22px; text-align: center; border: 1px solid #111; border-radius: 50%; padding: 1px 4px; }
        .sp-box-large { height: 60px; border: 1px solid #111; margin-left: 38px; }
        .sp-table { border-collapse: collapse; margin: 4px 0 0 38px; width: calc(100% - 38px); font-size: 9pt; }
        .sp-table th, .sp-table td { border: 1px solid #555; padding: 3px 4px; vertical-align: top; }
        .sp-table th { background: #f0f2f4; font-weight: bold; text-align: center; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .sp-table td.sp-cell { text-align: center; }
        .sp-table td.sp-write-cell { height: 22px; min-width: 60px; }
        .sp-table-plain td { border: none; }
        .sp-mt-label { width: 40%; }
        .sp-th-sub { font-weight: normal; font-size: 8pt; color: #444; }
        .sp-panel { margin: 4px 0; }
        .sp-panel-title { font-weight: bold; margin-top: 6px; }
        .sp-repeat { padding: 5px 0; border-bottom: 1px dotted #bbb; }
        .sp-entry { border: 1px solid #888; padding: 4px 8px; margin: 6px 0 6px 38px; }
        .sp-entry .sp-entry { margin-left: 20px; border-style: dashed; }
        .sp-entry-head { font-weight: bold; font-size: 9.5pt; background: #f0f2f4; margin: -4px -8px 4px; padding: 3px 8px;
            -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .sp-entry .sp-q:last-child { border-bottom: none; }
        @media print {
            body { background: #fff; }
            .sp-toolbar { display: none; }
            .sp-sheet { margin: 0; padding: 0; max-width: none; box-shadow: none; }
        }
    </style>
</head>
<body>
<div class="sp-toolbar">
    <a href="<?= e($backUrl) ?>">&larr; Back</a>
    <button type="button" class="primary" onclick="window.print()">Print / Save as PDF</button>
    <span>Tip: in the print dialog choose “Save as PDF” as the destination to download a PDF copy.</span>
</div>

<div class="sp-sheet">
    <div class="sp-form-head">
        <h1><?= e($formTitle) ?></h1>
        <div class="sp-version"><?= e($versionLabel) ?> · Paper form printed <?= e(date('d/m/Y')) ?></div>
        <?php if ($formDescription !== ''): ?>
        <p><?= e($formDescription) ?></p>
        <?php endif; ?>
    </div>

    <div class="sp-admin-box">
        <div>Data collector name: <span class="sp-fill"></span></div>
        <div>Date of collection: <span class="sp-fill"></span></div>
        <div>Paper form serial no.: <span class="sp-fill"></span></div>
        <div>Entered online by / date: <span class="sp-fill"></span></div>
    </div>

    <div class="sp-instructions">
        <strong>Instructions</strong>
        <ul>
            <li>Tick one box &#9744; unless the question says “tick all that apply”. Write clearly in block capitals.</li>
            <li>Questions marked <span class="sp-req">*</span> are required.</li>
            <li>Lines starting with &#8627; give a condition: answer that question only when the condition is met; otherwise skip it.</li>
            <li>Write-in questions (locations, facilities, medicines, pathogens) are coded from the standard lists when the form is entered online.</li>
        </ul>
    </div>

    <?= $formHtml ?>
</div>
</body>
</html>
