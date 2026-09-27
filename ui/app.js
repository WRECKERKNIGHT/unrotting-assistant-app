// Unrotting — Minimal Frontend
(function () {
    'use strict';

    let config = {};
    let stats = {};
    let timerInterval = null;
    let timeLeft = 45 * 60;
    let totalTime = 45 * 60;
    let isRunning = false;
    let isBreak = false;
    let sessionsCompleted = 0;
    let blockedApps = [];
    let canModify = true;
    let tasks = [];
    let isAdmin = false;

    const $ = id => document.getElementById(id);

    // ─── Toast System ───────────────────────────────────────────────────────

    function showToast(message, type = 'info') {
        const container = $('toast-container');
        const toast = document.createElement('div');
        const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    // ─── Splash & Init ────────────────────────────────────────────────────

    function showSplash() {
        $('splash-screen').classList.remove('hidden');
        setTimeout(() => {
            $('splash-screen').classList.add('hidden');
            checkPermission();
        }, 2000);
    }

    async function checkPermission() {
        if (!window.unrotting?.checkAdmin) {
            showPasswordScreen();
            return;
        }
        isAdmin = await window.unrotting.checkAdmin();
        if (!isAdmin) {
            $('permission-screen').classList.remove('hidden');
        } else {
            showPasswordScreen();
        }
    }

    async function requestAdmin() {
        try {
            const result = await window.unrotting.requestAdmin();
            if (result?.success) {
                isAdmin = true;
                $('permission-screen').classList.add('hidden');
                showToast('Admin access granted!', 'success');
                showPasswordScreen();
            } else {
                showToast('Admin access denied', 'error');
                showPasswordScreen();
            }
        } catch (e) {
            showToast('Failed to request admin', 'error');
            showPasswordScreen();
        }
    }

    function skipAdmin() {
        isAdmin = false;
        $('permission-screen').classList.add('hidden');
        showToast('Running with limited features', 'info');
        showPasswordScreen();
    }

    // ─── Password ───────────────────────────────────────────────────────────

    function showPasswordScreen() {
        config.has_password ?
            $('password-screen').classList.remove('hidden') :
            showMain();
    }

    async function verifyPassword(pw) {
        if (!config.has_password) return true;
        return await window.unrotting?.verifyPassword(pw) ?? true;
    }

    async function handlePasswordSubmit() {
        const pw = $('password-input').value;
        if (await verifyPassword(pw)) {
            showMain();
        } else {
            $('password-error').textContent = 'Incorrect password';
        }
    }

    async function handleSetPassword() {
        const np = $('new-password').value, cp = $('confirm-password').value;
        if (np.length < 4) { $('pw-error').textContent = 'Min 4 characters'; return; }
        if (np !== cp) { $('pw-error').textContent = 'Passwords do not match'; return; }
        await window.unrotting?.setPassword(np);
        config.has_password = true;
        $('password-screen').classList.remove('hidden');
        $('first-run-box').style.display = 'none';
        $('password-input').value = '';
        showToast('Password set successfully', 'success');
    }

    function showMain() {
        $('password-screen').classList.add('hidden');
        $('main-app').classList.remove('hidden');
        if (!isAdmin) $('admin-banner').classList.remove('hidden');
        loadStats();
        updateTimerDisplay();
        setupListeners();
    }

    // ─── Stats ──────────────────────────────────────────────────────────────

    async function loadStats() {
        if (!window.unrotting?.getStats) return;
        stats = await window.unrotting.getStats();
        renderStats();
        renderSummary();
        renderHeader();
    }

    function renderStats() {
        $('stat-blocked').textContent = stats.today_blocked || 0;
        $('stat-focus').textContent = Math.round(stats.today_focus_minutes || 0) + 'm';
        $('stat-streak').textContent = stats.streak_days || 0;
        $('stat-total').textContent = stats.total_sessions || 0;

        const blocks = stats.recent_blocks || [];
        if (!blocks.length) {
            $('activity-log').innerHTML = '<p class="note" style="margin:0;text-align:center;padding:1rem 0;">No blocks yet</p>';
        } else {
            $('activity-log').innerHTML = blocks.slice().reverse().map(b => `
                <div class="log-item">
                    <span>${esc(b.url)}</span>
                    <span class="log-time">${fmtTime(b.time)}</span>
                </div>
            `).join('');
        }
    }

    function renderSummary() {
        $('points-today').textContent = stats.points_today || 0;
        $('minutes-earned').textContent = Math.round(stats.minutes_earned_today || 0);
        $('tasks-done').textContent = stats.total_completions || 0;
        $('focus-time').textContent = Math.round(stats.today_focus_minutes || 0) + 'm';
    }

    function renderHeader() {
        $('header-points').textContent = stats.total_points || 0;
        $('header-streak').textContent = stats.streak_days || 0;
    }

    // ─── Tasks ──────────────────────────────────────────────────────────────

    async function loadTasks() {
        if (!window.unrotting?.getTasks) return;
        tasks = await window.unrotting.getTasks();
        renderTasks();
    }

    function renderTasks() {
        if (!tasks.length) {
            $('tasks-list').innerHTML = '<li class="empty">No tasks yet</li>';
            return;
        }
        $('tasks-list').innerHTML = tasks.map(t => `
            <li class="list-item">
                <div>
                    <div class="list-item-title">${esc(t.title)}</div>
                    <div class="list-item-sub">+${t.points || 50}pts / +${t.reward_minutes || 15}min</div>
                </div>
                ${canModify ? `<button class="complete-btn" data-id="${t.id}">✓</button>` : ''}
            </li>
        `).join('');
        document.querySelectorAll('.complete-btn').forEach(btn => {
            btn.addEventListener('click', () => completeTask(btn.dataset.id));
        });
    }

    async function addTask() {
        const title = $('task-input').value.trim();
        if (!title) return;
        await window.unrotting?.addTask(title);
        $('task-input').value = '';
        await loadTasks();
        await loadStats();
        showToast('Task added', 'success');
    }

    async function completeTask(id) {
        await window.unrotting?.completeTask(id);
        await loadTasks();
        await loadStats();
        showToast('Task completed! Points earned', 'success');
    }

    // ─── Blocked Apps ───────────────────────────────────────────────────────

    function loadBlockedApps() {
        blockedApps = config.blocked_apps || [];
        renderBlockedApps();
    }

    function renderBlockedApps() {
        if (!blockedApps.length) {
            $('blocked-apps-list').innerHTML = '<li class="empty">No apps blocked</li>';
            return;
        }
        $('blocked-apps-list').innerHTML = blockedApps.map((app, i) => `
            <li class="list-item">
                <span class="list-item-title">${esc(app)}</span>
                ${canModify ? `<button class="remove-btn" data-idx="${i}">×</button>` : ''}
            </li>
        `).join('');
        document.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', () => removeApp(parseInt(btn.dataset.idx)));
        });
    }

    function addApp() {
        if (!canModify) { showToast('Cannot modify during session', 'error'); return; }
        const app = $('custom-app-input').value.trim().toLowerCase();
        if (!app) return;
        if (blockedApps.includes(app)) { showToast('Already in list', 'error'); return; }
        blockedApps.push(app);
        $('custom-app-input').value = '';
        renderBlockedApps();
        window.unrotting?.setConfig({ blocked_apps: blockedApps });
        showToast('App added', 'success');
    }

    function removeApp(idx) {
        if (!canModify) { showToast('Cannot modify during session', 'error'); return; }
        blockedApps.splice(idx, 1);
        renderBlockedApps();
        window.unrotting?.setConfig({ blocked_apps: blockedApps });
    }

    // ─── Timer ──────────────────────────────────────────────────────────────

    function toggleTimer() { isRunning ? pauseTimer() : startTimer(); }

    async function startTimer() {
        isRunning = true;
        $('start-btn').textContent = 'Pause';
        $('start-btn').className = 'btn btn-secondary btn-large';

        if (!isBreak) {
            canModify = false;
            renderBlockedApps();
            renderTasks();
            await window.unrotting?.start_session();
            showToast('Focus session started', 'info');
        } else {
            canModify = true;
            renderBlockedApps();
            renderTasks();
            await window.unrotting?.start_break();
        }

        timerInterval = setInterval(() => {
            timeLeft--;
            updateTimerDisplay();
            if (timeLeft <= 0) { clearInterval(timerInterval); timerComplete(); }
        }, 1000);
    }

    function pauseTimer() {
        isRunning = false;
        clearInterval(timerInterval);
        $('start-btn').textContent = isBreak ? 'Resume Break' : 'Resume Focus';
        $('start-btn').className = 'btn btn-primary btn-large';
    }

    async function timerComplete() {
        if (isBreak) {
            isBreak = false;
            sessionsCompleted++;
            timeLeft = 45 * 60; totalTime = timeLeft;
            $('timer-label').textContent = 'Focus';
            $('start-btn').textContent = 'Start Focus';
            $('progress-ring').classList.remove('break');
            canModify = false;
            renderBlockedApps(); renderTasks();
            await window.unrotting?.end_break();
        } else {
            isBreak = true;
            timeLeft = 15 * 60; totalTime = timeLeft;
            $('timer-label').textContent = 'Break';
            $('start-btn').textContent = 'Start Break';
            $('progress-ring').classList.add('break');
            canModify = true;
            renderBlockedApps(); renderTasks();
            await window.unrotting?.start_break();
            showToast('Break time! Complete tasks to earn bonus', 'info');
        }
        updateTimerDisplay();
        await loadStats();
    }

    function skipBreak() {
        if (!isBreak || !isRunning) return;
        showConfirm('Skip break and start next focus session?', async () => {
            isBreak = false;
            sessionsCompleted++;
            timeLeft = 45 * 60; totalTime = timeLeft;
            $('timer-label').textContent = 'Focus';
            $('start-btn').textContent = 'Start Focus';
            $('progress-ring').classList.remove('break');
            canModify = false;
            renderBlockedApps(); renderTasks();
            await window.unrotting?.end_break();
        });
    }

    function updateTimerDisplay() {
        const m = Math.floor(timeLeft / 60), s = timeLeft % 60;
        $('timer-digits').textContent = `${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        const progress = totalTime > 0 ? (totalTime - timeLeft) / totalTime : 0;
        $('progress-ring').style.strokeDashoffset = 565 * (1 - progress);
        document.title = isBreak ? `${m}:${String(s).padStart(2,'0')} — Break` : `${m}:${String(s).padStart(2,'0')} — Focus`;
    }

    // ─── Settings ───────────────────────────────────────────────────────────

    function openSettings() {
        $('toggle-youtube-shorts').checked = config.block_youtube_shorts !== false;
        $('toggle-reels').checked = config.block_reels !== false;
        $('toggle-tiktok').checked = config.block_tiktok !== false;
        $('toggle-instagram').checked = config.block_instagram === true;
        $('toggle-strict').checked = config.strict_mode !== false;
        $('settings-modal').classList.remove('hidden');
    }

    function closeSettings() { $('settings-modal').classList.add('hidden'); }

    async function saveSettings() {
        await window.unrotting?.setConfig({
            block_youtube_shorts: $('toggle-youtube-shorts').checked,
            block_reels: $('toggle-reels').checked,
            block_tiktok: $('toggle-tiktok').checked,
            block_instagram: $('toggle-instagram').checked,
            strict_mode: $('toggle-strict').checked,
        });
        closeSettings();
        showToast('Settings saved', 'success');
    }

    // ─── Password Modal ─────────────────────────────────────────────────────

    function openPwModal() { $('password-modal').classList.remove('hidden'); }
    function closePwModal() {
        $('password-modal').classList.add('hidden');
        ['current-pw','new-pw','confirm-pw'].forEach(id => $(id).value = '');
        $('pw-modal-error').textContent = '';
    }

    async function handleChangePw() {
        const cur = $('current-pw').value, np = $('new-pw').value, cp = $('confirm-pw').value;
        if (!await verifyPassword(cur)) { $('pw-modal-error').textContent = 'Wrong password'; return; }
        if (np.length < 4) { $('pw-modal-error').textContent = 'Min 4 characters'; return; }
        if (np !== cp) { $('pw-modal-error').textContent = 'Passwords do not match'; return; }
        await window.unrotting?.setPassword(np);
        config.has_password = true;
        $('pw-modal-error').textContent = 'Updated!';
        setTimeout(closePwModal, 1200);
        showToast('Password updated', 'success');
    }

    // ─── Maintenance ────────────────────────────────────────────────────────

    async function backupHosts() {
        await window.unrotting?.backupHosts();
        showToast('Hosts file backed up', 'success');
    }

    async function restoreHosts() {
        showConfirm('Restore hosts file? This will undo all blocking.', async () => {
            await window.unrotting?.restoreHosts();
            showToast('Hosts file restored', 'success');
        });
    }

    async function resetStats() {
        showConfirm('Reset all statistics? This cannot be undone.', async () => {
            await window.unrotting?.resetStats();
            await loadStats();
            showToast('Statistics reset', 'success');
        });
    }

    async function resetTasks() {
        showConfirm('Reset all tasks and points? This cannot be undone.', async () => {
            await window.unrotting?.resetTasks();
            tasks = [];
            renderTasks();
            await loadStats();
            showToast('Tasks and points reset', 'success');
        });
    }

    // ─── Confirm Dialog ─────────────────────────────────────────────────────

    function showConfirm(msg, onConfirm) {
        $('confirm-message').textContent = msg;
        $('confirm-dialog').classList.remove('hidden');
        $('confirm-yes').onclick = () => { $('confirm-dialog').classList.add('hidden'); onConfirm(); };
        $('confirm-no').onclick = () => { $('confirm-dialog').classList.add('hidden'); };
        $('confirm-close').onclick = () => { $('confirm-dialog').classList.add('hidden'); };
    }

    // ─── About ──────────────────────────────────────────────────────────────

    function openAbout() { $('about-modal').classList.remove('hidden'); }
    function closeAbout() { $('about-modal').classList.add('hidden'); }

    // ─── Helpers ────────────────────────────────────────────────────────────

    function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

    function fmtTime(iso) {
        try { return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
        catch { return ''; }
    }

    // ─── Event Listeners ────────────────────────────────────────────────────

    function setupListeners() {
        // Permission
        $('admin-btn').addEventListener('click', requestAdmin);
        $('skip-admin-btn').addEventListener('click', skipAdmin);

        // Password
        $('password-btn').addEventListener('click', handlePasswordSubmit);
        $('password-input').addEventListener('keypress', e => { if (e.key === 'Enter') handlePasswordSubmit(); });
        $('set-password-btn').addEventListener('click', handleSetPassword);
        $('confirm-password').addEventListener('keypress', e => { if (e.key === 'Enter') handleSetPassword(); });
        $('about-btn').addEventListener('click', openAbout);

        // Timer
        $('start-btn').addEventListener('click', toggleTimer);
        $('skip-btn').addEventListener('click', skipBreak);

        // Settings
        $('settings-btn').addEventListener('click', openSettings);
        $('close-settings').addEventListener('click', closeSettings);
        $('save-settings').addEventListener('click', saveSettings);

        // Lock
        $('lock-btn').addEventListener('click', () => {
            $('main-app').classList.add('hidden');
            $('password-screen').classList.remove('hidden');
            $('password-input').value = '';
            $('password-error').textContent = '';
        });

        // Password modal
        $('change-password-btn').addEventListener('click', openPwModal);
        $('close-password').addEventListener('click', closePwModal);
        $('save-password-btn').addEventListener('click', handleChangePw);

        // Maintenance
        $('backup-hosts-btn').addEventListener('click', backupHosts);
        $('restore-hosts-btn').addEventListener('click', restoreHosts);
        $('reset-stats-btn').addEventListener('click', () => showConfirm('Reset all statistics?', resetStats));
        $('reset-tasks-btn').addEventListener('click', () => showConfirm('Reset tasks & points?', resetTasks));

        // Tasks
        $('add-task-btn').addEventListener('click', addTask);
        $('task-input').addEventListener('keypress', e => { if (e.key === 'Enter') addTask(); });

        // Blocked apps
        $('add-app-btn').addEventListener('click', addApp);
        $('custom-app-input').addEventListener('keypress', e => { if (e.key === 'Enter') addApp(); });

        // About
        $('close-about').addEventListener('click', closeAbout);
        $('open-repo-btn').addEventListener('click', e => {
            e.preventDefault();
            window.open('https://github.com/WRECKERKNIGHT/unrotting-assistant-app', '_blank');
        });
    }

    // ─── Init ───────────────────────────────────────────────────────────────

    function init() {
        loadConfig().then(cfg => {
            config = cfg;
            showSplash();
        });
    }

    async function loadConfig() {
        if (window.unrotting?.getConfig) return await window.unrotting.getConfig();
        return {
            block_youtube_shorts: true, block_reels: true, block_tiktok: true,
            block_instagram: false, focus_duration_minutes: 45, break_duration_minutes: 15,
            long_break_interval: 4, strict_mode: true, has_password: false, blocked_apps: []
        };
    }

    // Wait for pywebview
    if (window.pywebview) init();
    else window.addEventListener('pywebviewready', init);
})();

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !isBreak && isRunning) {
            // Don't allow escape during focus session
            e.preventDefault();
            showToast('Cannot close during focus session', 'error');
        }
        if (e.code === 'Space' && $('main-app').classList.contains('screen')) {
            e.preventDefault();
            toggleTimer();
        }
    });

const focusQuotes = [
    "The secret of getting ahead is getting started.",
    "It always seems impossible until it's done.",
    "Focus on being productive instead of busy.",
    "Your future is created by what you do today.",
    "The only way to do great work is to love what you do.",
    "Don't watch the clock; do what it does. Keep going.",
    "Success is the sum of small efforts repeated daily.",
    "What you get by achieving your goals is not as important as what you become."
];

function getRandomQuote() {
    return focusQuotes[Math.floor(Math.random() * focusQuotes.length)];
}
