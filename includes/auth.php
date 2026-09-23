<?php
/**
 * Authentication helpers
 */

/**
 * Attempt login with username and password
 */
function attemptLogin(string $username, string $password): bool
{
    $db = getDb();
    $stmt = $db->prepare(
        'SELECT id, full_name, username, password_hash, role, status
         FROM users WHERE username = ? LIMIT 1'
    );
    $stmt->execute([trim($username)]);
    $user = $stmt->fetch();

    if (!$user || $user['status'] !== 'active') {
        return false;
    }

    if (!password_verify($password, $user['password_hash'])) {
        return false;
    }

    session_regenerate_id(true);
    $_SESSION['user_id'] = (int) $user['id'];
    $_SESSION['user'] = [
        'id'        => (int) $user['id'],
        'full_name' => $user['full_name'],
        'username'  => $user['username'],
        'role'      => $user['role'],
    ];
    $_SESSION['created'] = time();

    return true;
}

/**
 * Log out current user
 */
function logoutUser(): void
{
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
    }
    session_destroy();
}

/**
 * Check if user is logged in
 */
function isLoggedIn(): bool
{
    return !empty($_SESSION['user_id']) && !empty($_SESSION['user']);
}

/**
 * Get current user array or null
 */
function currentUser(): ?array
{
    return $_SESSION['user'] ?? null;
}

/**
 * Get current user id
 */
function currentUserId(): ?int
{
    return isset($_SESSION['user_id']) ? (int) $_SESSION['user_id'] : null;
}

/**
 * Check if current user has one of the given roles
 */
function hasRole(...$roles): bool
{
    $user = currentUser();
    if (!$user) {
        return false;
    }
    return in_array($user['role'], $roles, true);
}
