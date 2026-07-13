/**
 * East Eagle Admin — day / night theme toggle
 */
(function () {
    var STORAGE_KEY = 'ee-admin-theme';

    function getTheme() {
        try {
            var saved = localStorage.getItem(STORAGE_KEY);
            if (saved === 'light' || saved === 'dark') {
                return saved;
            }
        } catch (e) {
            /* ignore */
        }
        return 'dark';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.body.classList.toggle('ee-theme-light', theme === 'light');
        document.body.classList.toggle('ee-theme-dark', theme === 'dark');

        document.querySelectorAll('.ee-theme-toggle').forEach(function (btn) {
            var isLight = theme === 'light';
            btn.setAttribute('aria-pressed', isLight ? 'true' : 'false');
            btn.setAttribute('aria-label', isLight ? 'Switch to night mode' : 'Switch to day mode');
            btn.title = isLight ? 'Night mode' : 'Day mode';
            var label = btn.querySelector('.ee-theme-label');
            if (label) {
                label.textContent = isLight ? 'Night' : 'Day';
            }
        });
    }

    function saveTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            /* ignore */
        }
    }

    function toggleTheme() {
        var next = getTheme() === 'light' ? 'dark' : 'light';
        applyTheme(next);
        saveTheme(next);
    }

    window.eeAdminToggleTheme = toggleTheme;

    document.addEventListener('DOMContentLoaded', function () {
        applyTheme(getTheme());

        document.querySelectorAll('.ee-theme-toggle').forEach(function (btn) {
            btn.addEventListener('click', toggleTheme);
        });
    });
})();
