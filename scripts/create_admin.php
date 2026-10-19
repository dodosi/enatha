<?php
/**
 * CLI script to create or reset super admin password
 * Usage: php scripts/create_admin.php
 * Optional: php scripts/create_admin.php admin "System Administrator" YourPassword123
 */

if (php_sapi_name() !== 'cli') {
    http_response_code(403);
    echo 'This script must be run from the command line: php scripts/create_admin.php';
    exit(1);
}

require_once dirname(__DIR__) . '/config/app.php';
require_once dirname(__DIR__) . '/config/database.php';

echo "Enatha - Create/Reset Super Admin Password\n";
echo "------------------------------------------\n";

// Non-interactive: php scripts/create_admin.php username "Full Name" password
if ($argc >= 4) {
    $username = trim($argv[1]);
    $fullName = trim($argv[2]);
    $password = $argv[3];
} else {
    $stdin = fopen('php://stdin', 'r');
    if ($stdin === false) {
        echo "Cannot read input. Use: php scripts/create_admin.php admin \"Full Name\" YourPassword\n";
        exit(1);
    }

    echo "Username [admin]: ";
    $username = trim(fgets($stdin)) ?: 'admin';
    echo "Full name [System Administrator]: ";
    $fullName = trim(fgets($stdin)) ?: 'System Administrator';
    echo "Password: ";
    $password = trim(fgets($stdin));
    fclose($stdin);
    echo "\n";
}

if ($username === '' || $fullName === '') {
    echo "Username and full name are required.\n";
    exit(1);
}

if (strlen($password) < 8) {
    echo "Password must be at least 8 characters.\n";
    exit(1);
}

$hash = password_hash($password, PASSWORD_DEFAULT);
$db = getDb();

$stmt = $db->prepare('SELECT id FROM users WHERE username = ?');
$stmt->execute([$username]);
$existing = $stmt->fetch();

$role = 'super_admin';
try {
    if ($existing) {
        $upd = $db->prepare(
            'UPDATE users SET full_name = ?, password_hash = ?, role = ?, leader_id = NULL, status = ? WHERE id = ?'
        );
        $upd->execute([$fullName, $hash, $role, 'active', $existing['id']]);
        echo "Super admin user updated successfully.\n";
    } else {
        $ins = $db->prepare(
            'INSERT INTO users (full_name, username, password_hash, role, leader_id, status) VALUES (?, ?, ?, ?, NULL, ?)'
        );
        $ins->execute([$fullName, $username, $hash, $role, 'active']);
        echo "Super admin user created successfully.\n";
    }
} catch (Throwable $e) {
    // Pre-migration fallback
    if ($existing) {
        $upd = $db->prepare('UPDATE users SET full_name = ?, password_hash = ?, role = ?, status = ? WHERE id = ?');
        $upd->execute([$fullName, $hash, 'admin', 'active', $existing['id']]);
        echo "Admin user updated (run database/migrations/001_leader_hierarchy.sql next).\n";
    } else {
        $ins = $db->prepare('INSERT INTO users (full_name, username, password_hash, role, status) VALUES (?, ?, ?, ?, ?)');
        $ins->execute([$fullName, $username, $hash, 'admin', 'active']);
        echo "Admin user created (run database/migrations/001_leader_hierarchy.sql next).\n";
    }
}
