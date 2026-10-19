<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdmin();

$db = getDb();
$error = '';
$isSuper = isSuperAdmin();
$selectedUserId = (int) ($_GET['user_id'] ?? $_POST['user_id'] ?? 0);

// Team members the current actor may assign surveys to
if ($isSuper) {
    $teamStmt = $db->query(
        "SELECT u.id, u.full_name, u.username, u.role, u.leader_id, u.restrict_surveys, l.full_name AS leader_name
         FROM users u
         LEFT JOIN users l ON l.id = u.leader_id
         WHERE u.role IN ('enumerator', 'supervisor') AND u.status = 'active'
         ORDER BY l.full_name, u.full_name"
    );
    $team = $teamStmt->fetchAll();
} else {
    $teamStmt = $db->prepare(
        "SELECT u.id, u.full_name, u.username, u.role, u.leader_id, u.restrict_surveys, NULL AS leader_name
         FROM users u
         WHERE u.leader_id = ? AND u.role IN ('enumerator', 'supervisor') AND u.status = 'active'
         ORDER BY u.full_name"
    );
    $teamStmt->execute([currentUserId()]);
    $team = $teamStmt->fetchAll();
}

$selected = null;
foreach ($team as $row) {
    if ((int) $row['id'] === $selectedUserId) {
        $selected = $row;
        break;
    }
}
if (!$selected && !empty($team)) {
    $selected = $team[0];
    $selectedUserId = (int) $selected['id'];
}

// Surveys owned by the selected user's leader (or current leader)
$ownerId = null;
if ($selected) {
    $ownerId = (int) ($selected['leader_id'] ?? 0);
}
if (!$ownerId && isLeader()) {
    $ownerId = currentUserId();
}

$surveys = [];
if ($ownerId > 0) {
    $sStmt = $db->prepare('SELECT id, survey_code, title FROM surveys WHERE owner_id = ? ORDER BY title');
    $sStmt->execute([$ownerId]);
    $surveys = $sStmt->fetchAll();
} elseif ($isSuper && $selected) {
    // Fallback if leader_id missing
    $surveys = [];
}

$assignedIds = [];
if ($selected) {
    $aStmt = $db->prepare('SELECT survey_id FROM user_survey_access WHERE user_id = ?');
    $aStmt->execute([$selectedUserId]);
    $assignedIds = array_map('intval', array_column($aStmt->fetchAll(), 'survey_id'));
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $selected) {
    if (!validateCsrf()) {
        $error = 'Invalid security token.';
    } elseif (!$isSuper && (int) $selected['leader_id'] !== currentUserId()) {
        $error = 'You can only assign surveys for your own team.';
    } else {
        $mode = $_POST['access_mode'] ?? 'all';
        $chosen = array_map('intval', $_POST['survey_ids'] ?? []);

        if ($mode === 'all') {
            $db->prepare('DELETE FROM user_survey_access WHERE user_id = ?')->execute([$selectedUserId]);
            $db->prepare('UPDATE users SET restrict_surveys = 0 WHERE id = ?')->execute([$selectedUserId]);
            // Refresh session if editing self (unlikely)
            setFlash('success', e($selected['full_name']) . ' can access all surveys from their leader.');
            redirect('admin/assign_surveys.php?user_id=' . $selectedUserId);
        } else {
            $validIds = array_map('intval', array_column($surveys, 'id'));
            $chosen = array_values(array_intersect($chosen, $validIds));
            if (empty($chosen)) {
                $error = 'Select at least one survey, or choose “All leader surveys”.';
            } else {
                $db->beginTransaction();
                try {
                    $db->prepare('DELETE FROM user_survey_access WHERE user_id = ?')->execute([$selectedUserId]);
                    $ins = $db->prepare('INSERT INTO user_survey_access (user_id, survey_id) VALUES (?, ?)');
                    foreach ($chosen as $sid) {
                        $ins->execute([$selectedUserId, $sid]);
                    }
                    $db->prepare('UPDATE users SET restrict_surveys = 1 WHERE id = ?')->execute([$selectedUserId]);
                    $db->commit();
                    setFlash('success', 'Survey access updated for ' . $selected['full_name'] . '.');
                    redirect('admin/assign_surveys.php?user_id=' . $selectedUserId);
                } catch (Throwable $e) {
                    $db->rollBack();
                    $error = 'Could not save assignments. Ensure the hierarchy migration has been applied.';
                }
            }
        }
    }
}

$pageTitle = 'Assign Surveys';
require dirname(__DIR__) . '/includes/layout_header.php';
$flash = getFlash();
$restrict = $selected ? !empty($selected['restrict_surveys']) : false;
?>
<?php if ($flash): ?>
<div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
<?php endif; ?>
<?php if ($error): ?>
<div class="alert alert-danger"><?= e($error) ?></div>
<?php endif; ?>

<div class="mb-4">
    <h1 class="h3 mb-1">Assign Surveys</h1>
    <p class="text-muted mb-0">
        By default, enumerators see <strong>all surveys created by their leader</strong>.
        Use this page only when someone should see a smaller subset.
    </p>
</div>

<?php if (empty($team)): ?>
<div class="alert alert-warning">No enumerators or supervisors to assign. Register team members first.</div>
<?php else: ?>

<div class="row g-4">
    <div class="col-md-4">
        <div class="card card-survey">
            <div class="card-header bg-white"><strong>Team member</strong></div>
            <div class="list-group list-group-flush">
                <?php foreach ($team as $row): ?>
                <a href="<?= e(url('admin/assign_surveys.php?user_id=' . (int) $row['id'])) ?>"
                   class="list-group-item list-group-item-action <?= (int) $row['id'] === $selectedUserId ? 'active' : '' ?>">
                    <div class="fw-semibold"><?= e($row['full_name']) ?></div>
                    <div class="small <?= (int) $row['id'] === $selectedUserId ? '' : 'text-muted' ?>">
                        <?= e($row['role']) ?>
                        <?php if (!empty($row['leader_name'])): ?> · <?= e($row['leader_name']) ?><?php endif; ?>
                    </div>
                </a>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
    <div class="col-md-8">
        <?php if ($selected): ?>
        <div class="card card-survey">
            <div class="card-header bg-white">
                <strong><?= e($selected['full_name']) ?></strong>
                <span class="text-muted small"> — survey access</span>
            </div>
            <div class="card-body">
                <?php if (empty($surveys)): ?>
                <div class="alert alert-info mb-0">
                    No surveys owned by this member’s leader yet. Upload a survey while logged in as that leader
                    (or as super admin assigning ownership).
                </div>
                <?php else: ?>
                <form method="post">
                    <?= csrfField() ?>
                    <input type="hidden" name="user_id" value="<?= (int) $selectedUserId ?>">

                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="access_mode" id="mode_all" value="all"
                                   <?= !$restrict ? 'checked' : '' ?>>
                            <label class="form-check-label" for="mode_all">
                                All surveys from their leader (default)
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="access_mode" id="mode_some" value="some"
                                   <?= $restrict ? 'checked' : '' ?>>
                            <label class="form-check-label" for="mode_some">
                                Only the surveys selected below
                            </label>
                        </div>
                    </div>

                    <div id="survey_checks" class="<?= $restrict ? '' : 'opacity-50' ?>">
                        <?php foreach ($surveys as $s): ?>
                        <div class="form-check">
                            <input class="form-check-input survey-cb" type="checkbox" name="survey_ids[]"
                                   value="<?= (int) $s['id'] ?>" id="s<?= (int) $s['id'] ?>"
                                   <?= in_array((int) $s['id'], $assignedIds, true) ? 'checked' : '' ?>>
                            <label class="form-check-label" for="s<?= (int) $s['id'] ?>">
                                <?= e($s['title']) ?>
                                <span class="text-muted small">(<?= e($s['survey_code']) ?>)</span>
                            </label>
                        </div>
                        <?php endforeach; ?>
                    </div>

                    <button type="submit" class="btn btn-primary mt-3">Save access</button>
                </form>
                <?php endif; ?>
            </div>
        </div>
        <?php endif; ?>
    </div>
</div>

<script>
(function () {
    var all = document.getElementById('mode_all');
    var some = document.getElementById('mode_some');
    var box = document.getElementById('survey_checks');
    if (!all || !box) return;
    function sync() {
        var restricted = some.checked;
        box.classList.toggle('opacity-50', !restricted);
        box.querySelectorAll('.survey-cb').forEach(function (cb) {
            cb.disabled = !restricted;
        });
    }
    all.addEventListener('change', sync);
    some.addEventListener('change', sync);
    sync();
})();
</script>
<?php endif; ?>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
