<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdmin();

$db = getDb();
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!validateCsrf()) {
        $error = 'Invalid security token.';
    } else {
        $action = $_POST['action'] ?? '';

        if ($action === 'toggle_status') {
            $userId = (int) ($_POST['user_id'] ?? 0);
            $newStatus = $_POST['new_status'] ?? '';
            if ($userId > 0 && in_array($newStatus, ['active', 'inactive'], true) && $userId !== currentUserId()) {
                $db->prepare('UPDATE users SET status = ? WHERE id = ?')->execute([$newStatus, $userId]);
                setFlash('success', 'User status updated.');
                redirect('admin/users.php');
            }
        } elseif ($action === 'reset_password') {
            $userId = (int) ($_POST['user_id'] ?? 0);
            $password = $_POST['new_password'] ?? '';
            if ($userId > 0 && strlen($password) >= 8) {
                $db->prepare('UPDATE users SET password_hash = ? WHERE id = ?')
                    ->execute([password_hash($password, PASSWORD_DEFAULT), $userId]);
                setFlash('success', 'Password reset successfully.');
                redirect('admin/users.php');
            } else {
                $error = 'Password must be at least 8 characters.';
            }
        }
    }
}

$users = $db->query(
    'SELECT id, full_name, username, role, status, created_at FROM users ORDER BY role, full_name'
)->fetchAll();

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
        <p class="text-muted mb-0">View users, activate/deactivate accounts, and reset passwords.</p>
    </div>
    <a href="<?= e(url('admin/register_user.php')) ?>" class="btn btn-primary">Register User</a>
</div>

<div class="card card-survey">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Username</th>
                            <th>Role</th>
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
                            <td>
                                <?php if ($u['status'] === 'active'): ?>
                                <span class="badge bg-success">Active</span>
                                <?php else: ?>
                                <span class="badge bg-secondary">Inactive</span>
                                <?php endif; ?>
                            </td>
                            <td class="small">
                                <?php if ((int) $u['id'] !== currentUserId()): ?>
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
                                <?php else: ?>
                                <span class="text-muted">(you)</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                        <?php endforeach; ?>
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
