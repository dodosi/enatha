<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdmin();

$db = getDb();
$error = '';
$isSuper = isSuperAdmin();

$userId = (int) ($_GET['id'] ?? $_POST['user_id'] ?? 0);
if ($userId <= 0) {
    setFlash('danger', 'User not found.');
    redirect('admin/users.php');
}

$stmt = $db->prepare(
    'SELECT id, full_name, username, role, leader_id, restrict_surveys, status
     FROM users WHERE id = ?'
);
$stmt->execute([$userId]);
$user = $stmt->fetch();

if (!$user) {
    setFlash('danger', 'User not found.');
    redirect('admin/users.php');
}

$isSelf = $userId === currentUserId();

if (!$isSelf && !canManageUserRow($user)) {
    setFlash('danger', 'You cannot manage that user.');
    redirect('admin/users.php');
}

// Leaders cannot edit other leaders / super_admins (canManageUserRow already blocks)
// Super admin editing themselves: limited fields
$allowedRoles = $isSuper
    ? ['leader', 'supervisor', 'enumerator']
    : ['supervisor', 'enumerator'];

if ($user['role'] === 'super_admin') {
    $allowedRoles = ['super_admin'];
} elseif ($isSelf && $user['role'] === 'leader') {
    $allowedRoles = ['leader'];
} elseif (!$isSuper && !in_array($user['role'], $allowedRoles, true)) {
    // Leader editing a team member whose role is already allowed
    $allowedRoles = array_values(array_unique(array_merge($allowedRoles, [$user['role']])));
}

$fullName = $user['full_name'];
$username = $user['username'];
$role = $user['role'];
$leaderId = $user['leader_id'] !== null ? (int) $user['leader_id'] : 0;
$status = $user['status'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!validateCsrf()) {
        $error = 'Invalid security token.';
    } else {
        $fullName = trim($_POST['full_name'] ?? '');
        $username = trim($_POST['username'] ?? '');
        $role = $_POST['role'] ?? $user['role'];
        $status = $_POST['status'] ?? $user['status'];
        $password = $_POST['password'] ?? '';
        $leaderId = (int) ($_POST['leader_id'] ?? 0);

        if ($fullName === '' || $username === '') {
            $error = 'Full name and username are required.';
        } elseif (!in_array($role, $allowedRoles, true)) {
            $error = 'Invalid role for your account.';
        } elseif (!in_array($status, ['active', 'inactive'], true)) {
            $error = 'Invalid status.';
        } elseif ($isSelf && $status === 'inactive') {
            $error = 'You cannot deactivate your own account.';
        } elseif ($password !== '' && strlen($password) < 8) {
            $error = 'New password must be at least 8 characters (or leave blank to keep current).';
        } else {
            $newLeaderId = null;
            if ($role === 'super_admin' || $role === 'leader') {
                $newLeaderId = null;
            } elseif ($isSuper) {
                if ($leaderId <= 0) {
                    $error = 'Select the leader this user belongs to.';
                } else {
                    $newLeaderId = $leaderId;
                }
            } else {
                // Leader editing their team member — keep under this leader
                $newLeaderId = currentUserId();
            }

            // Changing away from leader: ensure no team still attached
            if ($error === '' && $user['role'] === 'leader' && $role !== 'leader') {
                $cStmt = $db->prepare('SELECT COUNT(*) FROM users WHERE leader_id = ?');
                $cStmt->execute([$userId]);
                if ((int) $cStmt->fetchColumn() > 0) {
                    $error = 'Reassign or remove this leader’s team members before changing their role.';
                }
            }

            if ($error === '') {
                try {
                    if ($password !== '') {
                        $upd = $db->prepare(
                            'UPDATE users
                             SET full_name = ?, username = ?, role = ?, leader_id = ?, status = ?, password_hash = ?
                             WHERE id = ?'
                        );
                        $upd->execute([
                            $fullName,
                            $username,
                            $role,
                            $newLeaderId,
                            $status,
                            password_hash($password, PASSWORD_DEFAULT),
                            $userId,
                        ]);
                    } else {
                        $upd = $db->prepare(
                            'UPDATE users
                             SET full_name = ?, username = ?, role = ?, leader_id = ?, status = ?
                             WHERE id = ?'
                        );
                        $upd->execute([
                            $fullName,
                            $username,
                            $role,
                            $newLeaderId,
                            $status,
                            $userId,
                        ]);
                    }

                    // If role is no longer enumerator/supervisor, clear survey restrictions
                    if (!in_array($role, ['enumerator', 'supervisor'], true)) {
                        $db->prepare('DELETE FROM user_survey_access WHERE user_id = ?')->execute([$userId]);
                        $db->prepare('UPDATE users SET restrict_surveys = 0 WHERE id = ?')->execute([$userId]);
                    }

                    setFlash('success', 'User updated successfully.');
                    redirect('admin/users.php');
                } catch (PDOException $e) {
                    $error = strpos($e->getMessage(), 'Duplicate') !== false
                        ? 'Username already exists.'
                        : 'Could not update user.';
                }
            }
        }
    }
}

$leaders = [];
if ($isSuper) {
    $leaders = $db->query(
        "SELECT id, full_name, username FROM users
         WHERE role = 'leader' AND status = 'active' AND id <> " . (int) $userId . "
         ORDER BY full_name"
    )->fetchAll();
}

$pageTitle = 'Edit User';
require dirname(__DIR__) . '/includes/layout_header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h1 class="h3 mb-1">Edit User</h1>
        <p class="text-muted mb-0">Update account details for <?= e($user['full_name']) ?>.</p>
    </div>
    <a href="<?= e(url('admin/users.php')) ?>" class="btn btn-outline-secondary">Back to Users</a>
</div>

<?php if ($error): ?>
<div class="alert alert-danger"><?= e($error) ?></div>
<?php endif; ?>

<div class="row justify-content-center">
    <div class="col-lg-7 col-xl-6">
        <div class="card card-survey">
            <div class="card-header bg-white"><strong>Account Details</strong></div>
            <div class="card-body">
                <form method="post">
                    <?= csrfField() ?>
                    <input type="hidden" name="user_id" value="<?= (int) $userId ?>">
                    <div class="mb-3">
                        <label class="form-label" for="full_name">Full Name</label>
                        <input type="text" name="full_name" id="full_name" class="form-control" required
                               value="<?= e($fullName) ?>">
                    </div>
                    <div class="mb-3">
                        <label class="form-label" for="username">Username</label>
                        <input type="text" name="username" id="username" class="form-control" required
                               value="<?= e($username) ?>">
                    </div>
                    <div class="mb-3">
                        <label class="form-label" for="password">New Password</label>
                        <input type="password" name="password" id="password" class="form-control" minlength="8"
                               autocomplete="new-password">
                        <div class="form-text">Leave blank to keep the current password.</div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label" for="role">Role</label>
                        <select name="role" id="role" class="form-select" <?= count($allowedRoles) === 1 ? 'disabled' : '' ?>>
                            <?php foreach ($allowedRoles as $r): ?>
                            <option value="<?= e($r) ?>" <?= $role === $r ? 'selected' : '' ?>><?= e($r) ?></option>
                            <?php endforeach; ?>
                        </select>
                        <?php if (count($allowedRoles) === 1): ?>
                        <input type="hidden" name="role" value="<?= e($allowedRoles[0]) ?>">
                        <?php endif; ?>
                    </div>
                    <?php if ($isSuper && !in_array('super_admin', $allowedRoles, true)): ?>
                    <div class="mb-3" id="leader_pick_wrap">
                        <label class="form-label" for="leader_id">Leader (team)</label>
                        <select name="leader_id" id="leader_id" class="form-select">
                            <option value="">— Select leader —</option>
                            <?php foreach ($leaders as $L): ?>
                            <option value="<?= (int) $L['id'] ?>" <?= $leaderId === (int) $L['id'] ? 'selected' : '' ?>>
                                <?= e($L['full_name']) ?> (<?= e($L['username']) ?>)
                            </option>
                            <?php endforeach; ?>
                        </select>
                        <div class="form-text">Required for enumerator/supervisor. Cleared for leaders.</div>
                    </div>
                    <?php endif; ?>
                    <div class="mb-4">
                        <label class="form-label" for="status">Status</label>
                        <select name="status" id="status" class="form-select" <?= $isSelf ? 'disabled' : '' ?>>
                            <option value="active" <?= $status === 'active' ? 'selected' : '' ?>>Active</option>
                            <option value="inactive" <?= $status === 'inactive' ? 'selected' : '' ?>>Inactive</option>
                        </select>
                        <?php if ($isSelf): ?>
                        <input type="hidden" name="status" value="active">
                        <?php endif; ?>
                    </div>
                    <div class="d-flex gap-2 flex-wrap">
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                        <a href="<?= e(url('admin/users.php')) ?>" class="btn btn-outline-secondary">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<?php if ($isSuper && !in_array('super_admin', $allowedRoles, true)): ?>
<script>
(function () {
    var role = document.getElementById('role');
    var wrap = document.getElementById('leader_pick_wrap');
    if (!role || !wrap) return;
    function sync() {
        wrap.style.display = role.value === 'leader' ? 'none' : '';
    }
    role.addEventListener('change', sync);
    sync();
})();
</script>
<?php endif; ?>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
