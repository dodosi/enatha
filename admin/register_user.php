<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdmin();

$db = getDb();
$error = '';

$fullName = '';
$username = '';
$role = 'enumerator';

$isSuper = isSuperAdmin();
$allowedRoles = $isSuper
    ? ['leader', 'supervisor', 'enumerator']
    : ['supervisor', 'enumerator'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!validateCsrf()) {
        $error = 'Invalid security token.';
    } else {
        $fullName = trim($_POST['full_name'] ?? '');
        $username = trim($_POST['username'] ?? '');
        $password = $_POST['password'] ?? '';
        $role = $_POST['role'] ?? 'enumerator';

        if ($fullName === '' || $username === '' || strlen($password) < 8) {
            $error = 'Full name, username, and password (8+ chars) are required.';
        } elseif (!in_array($role, $allowedRoles, true)) {
            $error = 'Invalid role for your account.';
        } else {
            $leaderId = null;
            if ($role === 'leader') {
                $leaderId = null; // leaders head their own team
            } elseif ($isSuper) {
                // Super admin creating enumerator/supervisor must pick a leader
                $leaderId = (int) ($_POST['leader_id'] ?? 0);
                if ($leaderId <= 0) {
                    $error = 'Select the leader this user belongs to.';
                }
            } else {
                $leaderId = currentUserId();
            }

            if ($error === '') {
                try {
                    $ins = $db->prepare(
                        'INSERT INTO users (full_name, username, password_hash, role, leader_id, restrict_surveys, status)
                         VALUES (?, ?, ?, ?, ?, 0, ?)'
                    );
                    $ins->execute([
                        $fullName,
                        $username,
                        password_hash($password, PASSWORD_DEFAULT),
                        $role,
                        $leaderId,
                        'active',
                    ]);
                    setFlash('success', 'User registered successfully.');
                    redirect('admin/users.php');
                } catch (PDOException $e) {
                    $error = strpos($e->getMessage(), 'Duplicate') !== false
                        ? 'Username already exists.' : 'Could not register user. Run the leader hierarchy migration if you have not.';
                }
            }
        }
    }
}

$leaders = [];
if ($isSuper) {
    $leaders = $db->query(
        "SELECT id, full_name, username FROM users WHERE role = 'leader' AND status = 'active' ORDER BY full_name"
    )->fetchAll();
}

$pageTitle = 'Register User';
require dirname(__DIR__) . '/includes/layout_header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h1 class="h3 mb-1">Register User</h1>
        <p class="text-muted mb-0">
            <?php if ($isSuper): ?>
            Create a leader (team admin) or add enumerators/supervisors under a leader.
            <?php else: ?>
            Create an enumerator or supervisor for your team. They will see your surveys by default.
            <?php endif; ?>
        </p>
    </div>
    <a href="<?= e(url('admin/users.php')) ?>" class="btn btn-outline-secondary">View Users</a>
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
                        <label class="form-label" for="password">Temporary Password</label>
                        <input type="password" name="password" id="password" class="form-control" required minlength="8">
                        <div class="form-text">Use at least 8 characters.</div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label" for="role">Role</label>
                        <select name="role" id="role" class="form-select">
                            <?php if ($isSuper): ?>
                            <option value="leader" <?= $role === 'leader' ? 'selected' : '' ?>>Leader (team admin)</option>
                            <?php endif; ?>
                            <option value="enumerator" <?= $role === 'enumerator' ? 'selected' : '' ?>>Enumerator</option>
                            <option value="supervisor" <?= $role === 'supervisor' ? 'selected' : '' ?>>Supervisor</option>
                        </select>
                    </div>
                    <?php if ($isSuper): ?>
                    <div class="mb-4" id="leader_pick_wrap">
                        <label class="form-label" for="leader_id">Leader (team)</label>
                        <select name="leader_id" id="leader_id" class="form-select">
                            <option value="">— Select leader —</option>
                            <?php foreach ($leaders as $L): ?>
                            <option value="<?= (int) $L['id'] ?>"><?= e($L['full_name']) ?> (<?= e($L['username']) ?>)</option>
                            <?php endforeach; ?>
                        </select>
                        <div class="form-text">Required for enumerator/supervisor. Not used when creating a leader.</div>
                        <?php if (empty($leaders)): ?>
                        <div class="alert alert-warning mt-2 mb-0 py-2 small">No leaders yet. Create a Leader first, then add enumerators under them.</div>
                        <?php endif; ?>
                    </div>
                    <?php endif; ?>
                    <div class="d-flex gap-2 flex-wrap">
                        <button type="submit" class="btn btn-primary">Register User</button>
                        <a href="<?= e(url('admin/users.php')) ?>" class="btn btn-outline-secondary">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<?php if ($isSuper): ?>
<script>
(function () {
    var role = document.getElementById('role');
    var wrap = document.getElementById('leader_pick_wrap');
    function sync() {
        wrap.style.display = role.value === 'leader' ? 'none' : '';
    }
    role.addEventListener('change', sync);
    sync();
})();
</script>
<?php endif; ?>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
