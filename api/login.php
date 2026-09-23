<?php
require_once dirname(__DIR__) . '/includes/bootstrap.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonResponse(['success' => false, 'message' => 'Method not allowed'], 405);
}

requireCsrf();

$input = json_decode(file_get_contents('php://input'), true) ?: $_POST;
$username = trim($input['username'] ?? '');
$password = $input['password'] ?? '';

if ($username === '' || $password === '') {
    jsonResponse(['success' => false, 'message' => 'Username and password required'], 400);
}

if (!attemptLogin($username, $password)) {
    jsonResponse(['success' => false, 'message' => 'Invalid credentials'], 401);
}

$user = currentUser();
jsonResponse([
    'success' => true,
    'user'    => $user,
    'redirect' => $user['role'] === 'enumerator'
        ? url('surveys/select_survey.php')
        : url('admin/dashboard.php'),
]);
