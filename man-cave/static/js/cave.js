// man-cave — fluid drag-and-drop + resizable panels + auto-refresh

// ── Drag & Drop (fluid, with animation) ──────────────
(function() {
    let dragSrc = null;
    let dragGhost = null;

    function saveLayout() {
        const grid = document.getElementById('panelGrid');
        const order = [...grid.children]
            .filter(el => el.dataset.panel)
            .map(el => ({
                id: el.dataset.panel,
                span: el.dataset.span || '1'
            }));
        localStorage.setItem('cave-layout', JSON.stringify(order));
    }

    function restoreLayout() {
        const grid = document.getElementById('panelGrid');
        const saved = localStorage.getItem('cave-layout');
        if (!saved) return;
        try {
            const layout = JSON.parse(saved);
            const panels = {};
            [...grid.children].forEach(el => {
                if (el.dataset.panel) panels[el.dataset.panel] = el;
            });
            layout.forEach(item => {
                const panel = panels[item.id];
                if (panel) {
                    grid.appendChild(panel);
                    if (item.span && item.span !== '1') {
                        panel.dataset.span = item.span;
                        panel.style.gridColumn = `span ${item.span}`;
                    }
                }
            });
        } catch(e) {}
    }

    function getDropTarget(e) {
        const el = e.target.closest('.panel[data-panel]');
        return (el && el !== dragSrc) ? el : null;
    }

    function swapPanels(src, tgt) {
        const grid = document.getElementById('panelGrid');
        const panels = [...grid.children].filter(el => el.dataset.panel);
        const srcIdx = panels.indexOf(src);
        const tgtIdx = panels.indexOf(tgt);

        // Create a reference node for swapping
        const srcNext = src.nextSibling;
        const tgtNext = tgt.nextSibling;

        if (srcNext === tgt) {
            grid.insertBefore(tgt, src);
        } else if (tgtNext === src) {
            grid.insertBefore(src, tgt);
        } else {
            grid.insertBefore(src, tgtNext);
            grid.insertBefore(tgt, srcNext);
        }
    }

    function initDragDrop() {
        const grid = document.getElementById('panelGrid');
        if (!grid) return;

        restoreLayout();

        // Add resize handles to all panels
        grid.querySelectorAll('.panel[data-panel]').forEach(panel => {
            const handle = document.createElement('div');
            handle.className = 'panel-resize';
            handle.title = 'double-click to toggle wide';
            panel.appendChild(handle);

            // Double-click resize handle to toggle span
            handle.addEventListener('dblclick', e => {
                e.stopPropagation();
                const current = panel.dataset.span || '1';
                const next = current === '1' ? '2' : '1';
                panel.dataset.span = next;
                panel.style.gridColumn = next === '1' ? '' : `span ${next}`;
                panel.classList.add('drop-settle');
                setTimeout(() => panel.classList.remove('drop-settle'), 500);
                saveLayout();
            });
        });

        // Drag events
        grid.addEventListener('dragstart', e => {
            const panel = e.target.closest('.panel[data-panel]');
            if (!panel) return;
            dragSrc = panel;

            // Slight delay so the browser snapshot looks right
            requestAnimationFrame(() => {
                panel.classList.add('dragging');
            });

            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', panel.dataset.panel);
        });

        grid.addEventListener('dragend', e => {
            const panel = e.target.closest('.panel[data-panel]');
            if (panel) panel.classList.remove('dragging');
            grid.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
            dragSrc = null;
        });

        grid.addEventListener('dragover', e => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            const target = getDropTarget(e);

            // Clear previous highlights
            grid.querySelectorAll('.drag-over').forEach(el => {
                if (el !== target) el.classList.remove('drag-over');
            });

            if (target && !target.classList.contains('drag-over')) {
                target.classList.add('drag-over');
            }
        });

        grid.addEventListener('dragleave', e => {
            const target = e.target.closest('.panel[data-panel]');
            if (target && !target.contains(e.relatedTarget)) {
                target.classList.remove('drag-over');
            }
        });

        grid.addEventListener('drop', e => {
            e.preventDefault();
            const target = getDropTarget(e);
            if (!target || !dragSrc) return;

            target.classList.remove('drag-over');
            dragSrc.classList.remove('dragging');

            swapPanels(dragSrc, target);

            // Fluid settle animation on both
            [dragSrc, target].forEach(p => {
                p.classList.add('drop-settle');
                setTimeout(() => p.classList.remove('drop-settle'), 550);
            });

            saveLayout();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDragDrop);
    } else {
        initDragDrop();
    }
})();

// ── Auto-refresh dashboard every 10 seconds ──────────
setInterval(() => {
    fetch('/api/services')
        .then(r => r.json())
        .then(data => updateServices(data.services))
        .catch(() => {});

    fetch('/api/gpu')
        .then(r => r.json())
        .then(data => updateGPU(data))
        .catch(() => {});

    fetch('/api/lemonade')
        .then(r => r.json())
        .then(data => updateLemonade(data))
        .catch(() => {});
}, 10000);

function updateServices(services) {
    const rows = document.querySelectorAll('.service-row');
    services.forEach((svc, i) => {
        if (rows[i]) {
            const wasRunning = rows[i].classList.contains('running');
            const isRunning = svc.status === 'running';
            rows[i].className = `service-row ${isRunning ? 'running' : 'down'}`;
            rows[i].querySelector('.service-status').textContent = svc.status;
            rows[i].querySelector('.service-health').textContent = svc.health;
        }
    });
}

function updateGPU(gpu) {
    const values = document.querySelectorAll('.stat-value');
    if (values.length >= 5) {
        values[0].textContent = (gpu.gpu_temp || '?') + '°C';
        values[1].textContent = (gpu.gpu_util || '?') + '%';
        values[2].textContent = (gpu.cpu_percent || '?') + '%';
        values[3].textContent = gpu.load_avg || '?';
        values[4].textContent = `${gpu.ram_used_gb || '?'} / ${gpu.ram_total_gb || '?'} GB`;
    }
}

function updateLemonade(lm) {
    const panel = document.querySelector('.lemonade-panel');
    if (!panel) return;
    const rows = panel.querySelectorAll('.mono');
    if (rows.length >= 6) {
        rows[0].textContent = lm.status || '?';
        rows[0].className = `mono ${lm.status === 'online' ? 'text-green' : 'text-red'}`;
        rows[1].textContent = lm.model || '?';
        rows[2].textContent = lm.prompt_tps || '—';
        rows[3].textContent = lm.gen_tps || '—';
        rows[4].textContent = lm.slots_idle || '?';
        rows[5].textContent = lm.slots_processing || '?';
    }
}

async function freezeStack() {
    if (!confirm('Freeze the current AI stack state? This creates a snapshot you can roll back to.')) return;
    const btn = document.querySelector('.btn-freeze');
    btn.textContent = 'freezing...';
    btn.disabled = true;
    try {
        const resp = await fetch('/cave/api/freeze', { method: 'POST' });
        const data = await resp.json();
        btn.textContent = data.ok ? 'frozen!' : 'error';
        if (data.ok) setTimeout(() => location.reload(), 2000);
    } catch (e) {
        btn.textContent = 'error';
    }
    setTimeout(() => { btn.textContent = 'freeze stack'; btn.disabled = false; }, 3000);
}

async function thawStack() {
    if (!confirm('Restore AI stack from the LATEST frozen snapshot? Services will restart.')) return;
    const btn = document.querySelector('.btn-thaw');
    btn.textContent = 'thawing...';
    btn.disabled = true;
    try {
        const resp = await fetch('/cave/api/thaw', { method: 'POST' });
        const data = await resp.json();
        btn.textContent = data.ok ? 'restored!' : 'error';
        if (data.ok) setTimeout(() => location.reload(), 3000);
    } catch (e) {
        btn.textContent = 'error';
    }
    setTimeout(() => { btn.textContent = 'rollback latest'; btn.disabled = false; }, 4000);
}

async function thawSnapshot(name) {
    if (!confirm('Restore from snapshot: ' + name + '? Services will restart.')) return;
    try {
        const resp = await fetch('/cave/api/thaw', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({snapshot: name})
        });
        const data = await resp.json();
        if (data.ok) { alert('Restored from ' + name); location.reload(); }
        else alert('Restore failed');
    } catch (e) {
        alert('Error: ' + e);
    }
}

async function compileStack() {
    if (!confirm('Pull latest sources and compile? This will take several minutes. Services will restart when done.')) return;
    const btn = event.target;
    btn.textContent = 'compiling...';
    btn.disabled = true;
    btn.style.animation = 'pulse 1s infinite';
    try {
        const resp = await fetch('/cave/api/compile', { method: 'POST' });
        const data = await resp.json();
        btn.style.animation = '';
        btn.textContent = data.ok ? 'done!' : 'error: ' + (data.error || 'unknown');
        if (data.ok) setTimeout(() => location.reload(), 2000);
    } catch (e) {
        btn.style.animation = '';
        btn.textContent = 'error';
    }
    setTimeout(() => { btn.textContent = 'update & compile'; btn.disabled = false; }, 5000);
}

async function updateSources() {
    if (!confirm('Pull latest sources for all components? (does NOT compile)')) return;
    const btn = event.target;
    btn.textContent = 'pulling...';
    btn.disabled = true;
    try {
        const resp = await fetch('/cave/api/update-sources', { method: 'POST' });
        const data = await resp.json();
        btn.textContent = data.ok ? 'updated!' : 'error';
        if (data.ok) checkForUpdates(); // refresh indicators
    } catch (e) {
        btn.textContent = 'error';
    }
    setTimeout(() => { btn.textContent = 'pull sources'; btn.disabled = false; }, 3000);
}

// ── Stack update indicators ──────────────────────
async function checkForUpdates() {
    try {
        const resp = await fetch('/cave/api/update-check');
        const data = await resp.json();
        const rows = document.querySelectorAll('#stackList .stack-row');
        rows.forEach(row => {
            const nameEl = row.querySelector('span[style*="accent"]');
            if (!nameEl) return;
            const name = nameEl.textContent.trim();
            const update = data.updates[name];
            const dot = row.querySelector('.svc-dot');
            const verEl = row.querySelector('.mono[style*="text-align:right"]');

            if (update && update.has_update) {
                // Light up — update available
                row.style.background = 'rgba(255, 170, 0, 0.06)';
                row.style.borderLeft = '2px solid var(--orange)';
                if (verEl) {
                    verEl.style.color = 'var(--orange)';
                    verEl.textContent = verEl.textContent + ' ↑' + update.behind;
                }
                row.title = update.behind + ' commits behind upstream';
            } else {
                // Grey out — up to date
                row.style.background = '';
                row.style.borderLeft = '';
                row.style.opacity = '0.5';
                row.title = 'up to date';
            }
        });

        // Update the pull sources button if there are updates
        const pullBtn = document.querySelector('[onclick="updateSources()"]');
        if (pullBtn && data.any_updates) {
            pullBtn.style.borderColor = 'var(--orange)';
            pullBtn.style.color = 'var(--orange)';
            pullBtn.textContent = 'pull sources ●';
        }
    } catch (e) {
        // Silent fail — update check is non-critical
    }
}

// Check for updates on load and every 5 minutes
checkForUpdates();
setInterval(checkForUpdates, 300000);
