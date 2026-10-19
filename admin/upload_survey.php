<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdmin();

$db = getDb();
$scope = managedSurveysSql('s');
$surveySql = 'SELECT s.id, s.survey_code, s.title FROM surveys s WHERE 1=1' . $scope['sql'] . ' ORDER BY s.title';
$surveyStmt = $db->prepare($surveySql);
$surveyStmt->execute($scope['params']);
$surveys = $surveyStmt->fetchAll();

$error = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!validateCsrf()) {
        $error = 'Invalid security token.';
    } else {
        $surveyMode = $_POST['survey_mode'] ?? 'existing';
        $surveyId = (int) ($_POST['survey_id'] ?? 0);
        $surveyCode = trim($_POST['survey_code'] ?? '');
        $title = trim($_POST['title'] ?? '');
        $description = trim($_POST['description'] ?? '');
        $activate = !empty($_POST['activate_version']);
        $jsonContent = '';

        if (!empty($_FILES['json_file']['tmp_name']) && is_uploaded_file($_FILES['json_file']['tmp_name'])) {
            if ($_FILES['json_file']['size'] > MAX_UPLOAD_SIZE) {
                $error = 'File too large. Maximum ' . (MAX_UPLOAD_SIZE / 1024 / 1024) . 'MB.';
            } elseif (!in_array($_FILES['json_file']['type'], ['application/json', 'text/plain', 'application/octet-stream'], true)
                && pathinfo($_FILES['json_file']['name'], PATHINFO_EXTENSION) !== 'json') {
                $error = 'Only JSON files are allowed.';
            } else {
                $jsonContent = file_get_contents($_FILES['json_file']['tmp_name']);
            }
        } elseif (!empty($_POST['json_paste'])) {
            $jsonContent = trim($_POST['json_paste']);
        } else {
            $error = 'Please upload a JSON file or paste JSON content.';
        }

        if ($error === '' && !isValidSurveyJson($jsonContent)) {
            $error = 'Invalid SurveyJS JSON. Must contain "pages" or "elements".';
        }

        if ($error === '') {
            try {
                $db->beginTransaction();

                if ($surveyMode === 'new') {
                    if ($surveyCode === '' || $title === '') {
                        throw new RuntimeException('Survey code and title are required for new surveys.');
                    }
                    $check = $db->prepare('SELECT id FROM surveys WHERE survey_code = ?');
                    $check->execute([$surveyCode]);
                    if ($check->fetch()) {
                        throw new RuntimeException('Survey code already exists.');
                    }
                    // Leaders own their surveys; super admin owns surveys they create
                    $ownerId = isLeader() ? currentUserId() : currentUserId();
                    $ins = $db->prepare(
                        'INSERT INTO surveys (survey_code, title, description, owner_id) VALUES (?, ?, ?, ?)'
                    );
                    $ins->execute([$surveyCode, $title, $description ?: null, $ownerId]);
                    $surveyId = (int) $db->lastInsertId();
                } else {
                    if ($surveyId <= 0) {
                        throw new RuntimeException('Please select an existing survey.');
                    }
                    if (isLeader()) {
                        $own = $db->prepare('SELECT owner_id FROM surveys WHERE id = ?');
                        $own->execute([$surveyId]);
                        $row = $own->fetch();
                        if (!$row || (int) $row['owner_id'] !== currentUserId()) {
                            throw new RuntimeException('You can only add versions to surveys you own.');
                        }
                    }
                }

                $versionNumber = getNextVersionNumber($db, $surveyId);
                $status = $activate ? 'active' : 'inactive';

                if ($activate) {
                    $db->prepare('UPDATE survey_versions SET status = ? WHERE survey_id = ?')
                        ->execute(['inactive', $surveyId]);
                }

                $verIns = $db->prepare(
                    'INSERT INTO survey_versions (survey_id, version_number, json_definition, status, created_by)
                     VALUES (?, ?, ?, ?, ?)'
                );
                $verIns->execute([
                    $surveyId,
                    $versionNumber,
                    $jsonContent,
                    $status,
                    currentUserId(),
                ]);

                $db->commit();
                setFlash('success', "Survey version v{$versionNumber} uploaded successfully.");
                redirect('admin/surveys.php');
            } catch (Exception $e) {
                $db->rollBack();
                $error = $e->getMessage();
            }
        }
    }
}

$pageTitle = 'Upload Survey';
require dirname(__DIR__) . '/includes/layout_header.php';
?>
<h1 class="h3 mb-4">Upload Survey JSON</h1>

<?php if ($error): ?>
<div class="alert alert-danger"><?= e($error) ?></div>
<?php endif; ?>

<div class="card card-survey">
    <div class="card-body">
        <form method="post" enctype="multipart/form-data">
            <?= csrfField() ?>

            <div class="mb-3">
                <label class="form-label">Survey</label>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="survey_mode" id="mode_existing" value="existing" checked>
                    <label class="form-check-label" for="mode_existing">Add version to existing survey</label>
                </div>
                <div class="form-check mb-2">
                    <input class="form-check-input" type="radio" name="survey_mode" id="mode_new" value="new">
                    <label class="form-check-label" for="mode_new">Create new survey</label>
                </div>
                <select name="survey_id" id="survey_id" class="form-select">
                    <option value="">-- Select survey --</option>
                    <?php foreach ($surveys as $s): ?>
                    <option value="<?= (int) $s['id'] ?>"><?= e($s['title']) ?> (<?= e($s['survey_code']) ?>)</option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div id="new_survey_fields" class="d-none border rounded p-3 mb-3 bg-light">
                <div class="mb-2">
                    <label class="form-label" for="survey_code">Survey Code</label>
                    <input type="text" class="form-control" id="survey_code" name="survey_code" placeholder="e.g. HH_SURVEY">
                </div>
                <div class="mb-2">
                    <label class="form-label" for="title">Title</label>
                    <input type="text" class="form-control" id="title" name="title" placeholder="e.g. Household Survey">
                </div>
                <div class="mb-0">
                    <label class="form-label" for="description">Description</label>
                    <textarea class="form-control" id="description" name="description" rows="2"></textarea>
                </div>
            </div>

            <div class="mb-3">
                <label class="form-label" for="json_file">SurveyJS JSON File</label>
                <input type="file" class="form-control" id="json_file" name="json_file" accept=".json,application/json">
            </div>

            <div class="mb-3">
                <label class="form-label" for="json_paste">Or paste JSON</label>
                <textarea class="form-control font-monospace small" id="json_paste" name="json_paste" rows="8"
                          placeholder='{"pages": [...]}'></textarea>
            </div>

            <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" name="activate_version" id="activate_version" value="1" checked>
                <label class="form-check-label" for="activate_version">
                    Activate this version immediately (recommended for field use)
                </label>
            </div>

            <button type="submit" class="btn btn-primary">Upload Version</button>
            <a href="<?= e(url('admin/surveys.php')) ?>" class="btn btn-outline-secondary">Cancel</a>
        </form>
    </div>
</div>

<script>
document.querySelectorAll('input[name="survey_mode"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
        var isNew = document.getElementById('mode_new').checked;
        document.getElementById('new_survey_fields').classList.toggle('d-none', !isNew);
        document.getElementById('survey_id').disabled = isNew;
    });
});
</script>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
