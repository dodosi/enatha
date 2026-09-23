<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';
requireAdmin();

$db = getDb();
$error = '';

$fullName = '';
$username = '';
$role = 'enumerator';

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
        } elseif (!in_array($role, ['admin', 'supervisor', 'enumerator'], true)) {
            $error = 'Invalid role.';
        } else {
            try {
                $ins = $db->prepare(
                    'INSERT INTO users (full_name, username, password_hash, role, status) VALUES (?, ?, ?, ?, ?)'
                );
                $ins->execute([$fullName, $username, password_hash($password, PASSWORD_DEFAULT), $role, 'active']);
                setFlash('success', 'User registered successfully.');
                redirect('admin/users.php');
            } catch (PDOException $e) {
                $error = strpos($e->getMessage(), 'Duplicate') !== false
                    ? 'Username already exists.' : 'Could not register user.';
            }
        }
    }
}

$pageTitle = 'Register User';
require dirname(__DIR__) . '/includes/layout_header.php';
?>

<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
    <div>
        <h1 class="h3 mb-1">Register User</h1>
        <p class="text-muted mb-0">Create a new admin, supervisor, or enumerator account.</p>
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
                        <div class="form-text">Use at least 8 characters. The user can be reset later from the users page.</div>
                    </div>
                    <div class="mb-4">
                        <label class="form-label" for="role">Role</label>
                        <select name="role" id="role" class="form-select">
                            <option value="enumerator" <?= $role === 'enumerator' ? 'selected' : '' ?>>Enumerator</option>
                            <option value="supervisor" <?= $role === 'supervisor' ? 'selected' : '' ?>>Supervisor</option>
                            <option value="admin" <?= $role === 'admin' ? 'selected' : '' ?>>Admin</option>
                        </select>
                    </div>
                    <div class="d-flex gap-2 flex-wrap">
                        <button type="submit" class="btn btn-primary">Register User</button>
                        <a href="<?= e(url('admin/users.php')) ?>" class="btn btn-outline-secondary">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<?php require dirname(__DIR__) . '/includes/layout_footer.php'; ?>
