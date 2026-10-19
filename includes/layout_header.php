<?php
/** @var string $pageTitle */
$pageTitle = $pageTitle ?? APP_NAME;
$user = currentUser();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= e($pageTitle) ?> - <?= e(APP_NAME) ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="<?= e(url('assets/css/app.css')) ?>" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark app-navbar shadow-sm sticky-top">
    <div class="container-fluid">
        <a class="navbar-brand fw-semibold d-flex align-items-center" href="<?= e(url('index.php')) ?>">
            <span class="navbar-brand-mark">E</span>
            <span><?= e(APP_NAME) ?></span>
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navMain">
            <?php if ($user): ?>
            <ul class="navbar-nav me-auto">
                <?php if (canViewAdminDashboard()): ?>
                <li class="nav-item"><a class="nav-link" href="<?= e(url('admin/dashboard.php')) ?>">Dashboard</a></li>
                <li class="nav-item"><a class="nav-link" href="<?= e(url('admin/surveys.php')) ?>">Surveys</a></li>
                <li class="nav-item"><a class="nav-link" href="<?= e(url('admin/responses.php')) ?>">Responses</a></li>
                <?php if (canManageTeam()): ?>
                <li class="nav-item"><a class="nav-link" href="<?= e(url('admin/users.php')) ?>">Users</a></li>
                <li class="nav-item"><a class="nav-link" href="<?= e(url('admin/register_user.php')) ?>">Register User</a></li>
                <li class="nav-item"><a class="nav-link" href="<?= e(url('admin/assign_surveys.php')) ?>">Assign Surveys</a></li>
                <?php endif; ?>
                <?php endif; ?>
                <?php if (canTakeSurveys()): ?>
                <li class="nav-item"><a class="nav-link" href="<?= e(url('surveys/select_survey.php')) ?>">Take Survey</a></li>
                <?php endif; ?>
            </ul>
            <span class="navbar-text text-white-50 me-3 small d-none d-md-inline">
                <?= e($user['full_name']) ?> (<?= e($user['role']) ?>)
            </span>
            <a class="btn btn-outline-light btn-sm" href="<?= e(url('api/logout.php')) ?>">Logout</a>
            <?php else: ?>
            <ul class="navbar-nav me-auto"></ul>
            <span class="navbar-text text-white-50 me-3 small d-none d-md-inline">
                Institutional survey and field data collection
            </span>
            <a class="btn btn-outline-light btn-sm" href="<?= e(url('index.php')) ?>">Login</a>
            <?php endif; ?>
        </div>
    </div>
</nav>
<main class="container app-shell">
