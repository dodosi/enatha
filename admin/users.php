<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdmin();

$db = getDb();
$error = '';
$isSuper = isSuperAdmin();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!validateCsrf()) {
        $error = 'Invalid security token.';
    } else {
        $action = $_POST['action'] ?? '';
        $userId = (int) ($_POST['user_id'] ?? 0);

        $target = null;
        if ($userId > 0) {
            $tStmt = $db->prepare('SELECT id, role, leader_id FROM users WHERE id = ?');
            $tStmt->execute([$userId]);
            $target = $tStmt->fetch();
        }

        if (!$target || !canManageUserRow($target)) {
            // Super admin can manage anyone except cannot deactivate self (handled below)
            if (!$isSuper || !$target) {
                $error = 'You cannot manage that user.';
            }
        }

        if ($error === '' && $target) {
            if ($action === 'toggle_status') {
                $newStatus = $_POST['new_status'] ?? '';
                if ($userId > 0 && in_array($newStatus, ['active', 'inactive'], true) && $userId !== currentUserId()) {
                    if ($isSuper || canManageUserRow($target)) {
                        $db->prepare('UPDATE users SET status = ? WHERE id = ?')->execute([$newStatus, $userId]);
                        setFlash('success', 'User status updated.');
                        redirect('admin/users.php');
                    }
                }
            } elseif ($action === 'reset_password') {
                $password = $_POST['new_password'] ?? '';
                if ($userId > 0 && strlen($password) >= 8 && ($isSuper || canManageUserRow($target))) {
                    $db->prepare('UPDATE users SET password_hash = ? WHERE id = ?')
                        ->execute([password_hash($password, PASSWORD_DEFAULT), $userId]);
                    setFlash('success', 'Password reset successfully.');
                    redirect('admin/users.php');
                } else {
                    $error = 'Password must be at least 8 characters.';
                }
            } elseif ($action === 'delete_user') {
                if ($userId === currentUserId()) {
                    $error = 'You cannot delete your own account.';
                } elseif (($target['role'] ?? '') === 'super_admin') {
                    $error = 'Super admin accounts cannot be deleted.';
                } elseif (!$isSuper && !canManageUserRow($target)) {
                    $error = 'You cannot delete that user.';
                } else {
                    $teamStmt = $db->prepare('SELECT COUNT(*) FROM users WHERE leader_id = ?');
                    $teamStmt->execute([$userId]);
                    if ((int) $teamStmt->fetchColumn() > 0) {
                        $error = 'This leader still has team members. Reassign or delete them first.';
                    } else {
                        $respStmt = $db->prepare('SELECT COUNT(*) FROM responses WHERE enumerator_id = ?');
                        $respStmt->execute([$userId]);
                        if ((int) $respStmt->fetchColumn() > 0) {
                            $error = 'This user has survey responses. Deactivate them instead of deleting.';
                        } else {
                            try {
                                $db->prepare('DELETE FROM user_survey_access WHERE user_id = ?')->execute([$userId]);
                                $db->prepare('DELETE FROM drafts WHERE user_id = ?')->execute([$userId]);
                                // Surveys they own: clear owner (FK SET NULL) before delete if needed
                                $db->prepare('UPDATE surveys SET owner_id = NULL WHERE owner_id = ?')->execute([$userId]);
                                $db->prepare('DELETE FROM users WHERE id = ?')->execute([$userId]);
                                setFlash('success', 'User deleted.');
                                redirect('admin/users.php');
                            } catch (PDOException $e) {
                                $error = 'Could not delete user (linked records). Deactivate instead.';
                            }
                        }
                    }
                }
            }
        }
    }
}

if ($isSuper) {
    $users = $db->query(
        'SELECT u.id, u.full_name, u.username, u.role, u.status, u.created_at, u.leader_id,
                u.restrict_surveys, l.full_name AS leader_name
         FROM users u
         LEFT JOIN users l ON l.id = u.leader_id
         ORDER BY u.role, u.full_name'
    )->fetchAll();
} else {
    $stmt = $db->prepare(
        'SELECT u.id, u.full_name, u.username, u.role, u.status, u.created_at, u.leader_id,
                u.restrict_surveys, l.full_name AS leader_name
         FROM users u
         LEFT JOIN users l ON l.id = u.leader_id
         WHERE u.leader_id = ?
         ORDER BY u.role, u.full_name'
    );
    $stmt->execute([currentUserId()]);
    $users = $stmt->fetchAll();
}

$pageTitle = 'Users';
require dirname(__DIR__) . '/includes/layout_header.php';
$flash = getFlash();
?>
<?php if ($flash): ?>
<div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
<?php endif; ?>
<?php if ($error): ?>
<div class="alert alert-danger"><?= e($error) ?></div>
<?php endif; ?>

<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h1 class="h3 mb-1">Users</h1>
        <p class="text-muted mb-0">
            <?php if ($isSuper): ?>
            All accounts. Create leaders, then enumerators under each leader.
            <?php else: ?>
            Your team members. Assign surveys from the Assign Surveys page when you need to restrict access.
            <?php endif; ?>
        </p>
    </div>
    <div class="d-flex gap-2">
        <a href="<?= e(url('admin/assign_surveys.php')) ?>" class="btn btn-outline-primary">Assign Surveys</a>
        <a href="<?= e(url('admin/register_user.php')) ?>" class="btn btn-primary">Register User</a>
    </div>
</div>

<div class="card card-survey">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Username</th>
                            <th>Role</th>
                            <?php if ($isSuper): ?><th>Leader / team</th><?php endif; ?>
                            <th>Survey access</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($users as $u): ?>
                        <tr>
                            <td><?= e($u['full_name']) ?></td>
                            <td><?= e($u['username']) ?></td>
                            <td><span class="badge bg-info text-dark"><?= e($u['role']) ?></span></td>
                            <?php if ($isSuper): ?>
                            <td class="small"><?= e($u['leader_name'] ?? ($u['role'] === 'leader' || $u['role'] === 'super_admin' ? '—' : 'Unassigned')) ?></td>
                            <?php endif; ?>
                            <td class="small">
                                <?php if (in_array($u['role'], ['enumerator', 'supervisor'], true)): ?>
                                    <?= !empty($u['restrict_surveys']) ? 'Restricted list' : 'All leader surveys' ?>
                                <?php else: ?>
                                    —
                                <?php endif; ?>
                            </td>
                            <td>
                                <?php if ($u['status'] === 'active'): ?>
                                <span class="badge bg-success">Active</span>
                                <?php else: ?>
                                <span class="badge bg-secondary">Inactive</span>
                                <?php endif; ?>
                            </td>
                            <td class="small text-nowrap">
                                <a href="<?= e(url('admin/edit_user.php?id=' . (int) $u['id'])) ?>">Edit</a>
                                <?php if ((int) $u['id'] !== currentUserId()): ?>
                                ·
                                <form method="post" class="d-inline">
                                    <?= csrfField() ?>
                                    <input type="hidden" name="action" value="toggle_status">
                                    <input type="hidden" name="user_id" value="<?= (int) $u['id'] ?>">
                                    <input type="hidden" name="new_status" value="<?= $u['status'] === 'active' ? 'inactive' : 'active' ?>">
                                    <button type="submit" class="btn btn-link btn-sm p-0">
                                        <?= $u['status'] === 'active' ? 'Deactivate' : 'Activate' ?>
                                    </button>
                                </form>
                                ·
                                <button type="button" class="btn btn-link btn-sm p-0" data-bs-toggle="modal"
                                        data-bs-target="#resetModal" data-user-id="<?= (int) $u['id'] ?>"
                                        data-user-name="<?= e($u['full_name']) ?>">Reset password</button>
                                <?php if (in_array($u['role'], ['enumerator', 'supervisor'], true)): ?>
                                ·
                                <a href="<?= e(url('admin/assign_surveys.php?user_id=' . (int) $u['id'])) ?>">Surveys</a>
                                <?php endif; ?>
                                <?php if (($u['role'] ?? '') !== 'super_admin'): ?>
                                ·
                                <form method="post" class="d-inline"
                                      onsubmit="return confirm(<?= json_encode('Delete ' . $u['full_name'] . ' permanently? This cannot be undone.') ?>);">
                                    <?= csrfField() ?>
                                    <input type="hidden" name="action" value="delete_user">
                                    <input type="hidden" name="user_id" value="<?= (int) $u['id'] ?>">
                                    <button type="submit" class="btn btn-link btn-sm p-0 text-danger">Delete</button>
                                </form>
                                <?php endif; ?>
                                <?php else: ?>
                                <span class="text-muted"> (you)</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                        <?php if (empty($users)): ?>
                        <tr><td colspan="<?= $isSuper ? 7 : 6 ?>" class="text-muted text-center py-4">No users in this list yet.</td></tr>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>
</div>

<div class="modal fade" id="resetModal" tabindex="-1">
    <div class="modal-dialog">
        <form method="post" class="modal-content">
            <?= csrfField() ?>
            <input type="hidden" name="action" value="reset_password">
            <input type="hidden" name="user_id" id="reset_user_id">
            <div class="modal-header">
                <h5 class="modal-title">Reset Password</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p class="small text-muted">User: <span id="reset_user_name"></span></p>
                <label class="form-label">New password (min 8 chars)</label>
                <input type="password" name="new_password" class="form-control" required minlength="8">
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">Reset</button>
            </div>
        </form>
    </div>
</div>

<script>
document.getElementById('resetModal').addEventListener('show.bs.modal', function (e) {
    var btn = e.relatedTarget;
    document.getElementById('reset_user_id').value = btn.getAttribute('data-user-id');
    document.getElementById('reset_user_name').textContent = btn.getAttribute('data-user-name');
});
</script>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
