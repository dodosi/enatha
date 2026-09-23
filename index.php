<?php
require_once __DIR__ . '/includes/bootstrap.php';

if (isLoggedIn()) {
    $user = currentUser();
    if ($user['role'] === 'enumerator') {
        redirect('surveys/select_survey.php');
    }
    redirect('admin/dashboard.php');
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!validateCsrf()) {
        $error = 'Invalid security token. Please refresh and try again.';
    } else {
        $username = trim($_POST['username'] ?? '');
        $password = $_POST['password'] ?? '';
        if ($username === '' || $password === '') {
            $error = 'Please enter username and password.';
        } elseif (attemptLogin($username, $password)) {
            $user = currentUser();
            if ($user['role'] === 'enumerator') {
                redirect('surveys/select_survey.php');
            }
            redirect('admin/dashboard.php');
        } else {
            $error = 'Invalid username or password.';
        }
    }
}

$pageTitle = 'Login';
require __DIR__ . '/includes/layout_header.php';
?>
<div class="login-card card">
    <div class="login-hero text-center">
        <div class="brand-badge">E</div>
        <h1 class="h4 mb-2"><?= e(APP_NAME) ?></h1>
        <p class="mb-0 small opacity-75">Research-grade survey and field data collection</p>
    </div>
    <div class="card-body">
        <p class="text-muted text-center small mb-4">Sign in to continue</p>
        <?php if ($error): ?>
        <div class="alert alert-danger py-2"><?= e($error) ?></div>
        <?php endif; ?>
        <form method="post" action="">
            <?= csrfField() ?>
            <div class="mb-3">
                <label class="form-label" for="username">Username</label>
                <input type="text" class="form-control" id="username" name="username" required autofocus
                       value="<?= e($_POST['username'] ?? '') ?>">
            </div>
            <div class="mb-3">
                <label class="form-label" for="password">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Sign In</button>
        </form>
    </div>
</div>
<?php require __DIR__ . '/includes/layout_footer.php'; ?>
