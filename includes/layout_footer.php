
</main>
<footer class="app-footer text-center small py-3 border-top">
    &copy; <?= date('Y') ?> <?= e(APP_NAME) ?> v<?= e(APP_VERSION) ?> · Institutional Data Collection
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<?php if (!empty($extraScripts)): ?>
<?= $extraScripts ?>
<?php endif; ?>
</body>
</html>
