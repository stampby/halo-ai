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


// ── Agent Status — live dots from activity feed ─────
function updateAgentDots(data) {
    const lastAct = data.last_activity || {};
    const now = Date.now();
    document.querySelectorAll('.agent-row[data-agent]').forEach(row => {
        const name = row.dataset.agent;
        const dot = row.querySelector('.svc-dot');
        if (!dot) return;
        const lastTime = lastAct[name];
        if (!lastTime) { dot.className = 'svc-dot unknown'; return; }
        const age = now - new Date(lastTime).getTime();
        const tenMin = 10 * 60 * 1000;
        const oneHour = 60 * 60 * 1000;
        dot.className = 'svc-dot ' + (age < tenMin ? 'up' : age < oneHour ? 'unknown' : 'down');
    });
    // Also update the family tree agt dots
    document.querySelectorAll('.agt').forEach(agt => {
        const nameEl = agt.querySelector('.agt-name');
        if (!nameEl) return;
        const name = nameEl.textContent.trim();
        const dot = agt.querySelector('.svc-dot');
        if (!dot) return;
        const lastTime = lastAct[name];
        if (!lastTime) { dot.className = 'svc-dot unknown'; return; }
        const age = now - new Date(lastTime).getTime();
        const tenMin = 10 * 60 * 1000;
        const oneHour = 60 * 60 * 1000;
        dot.className = 'svc-dot ' + (age < tenMin ? 'up' : age < oneHour ? 'unknown' : 'down');
    });
}

// Poll agent status every 10 seconds
setInterval(() => {
    fetch('/cave/api/agents/status')
        .then(r => r.json())
        .then(data => updateAgentDots(data))
        .catch(() => {});
}, 10000);
// Initial fetch
fetch('/cave/api/agents/status').then(r => r.json()).then(data => updateAgentDots(data)).catch(() => {});


// ── Kansas City Shuffle — Ring Bus ──────────────────
async function kcsRefresh() {
    try {
        const r = await fetch('/cave/api/kcs/status');
        const d = await r.json();

        // Update machine dots + latency
        for (const [name, m] of Object.entries(d.machines)) {
            const dot = document.getElementById('kcs-dot-' + name);
            const lat = document.getElementById('kcs-latency-' + name);
            if (dot) {
                dot.className = 'svc-dot ' + (m.status === 'up' ? 'up' : m.status === 'degraded' ? 'unknown' : 'down');
            }
            if (lat && m.ssh) {
                lat.textContent = m.ssh.reachable ? m.ssh.latency_ms + 'ms' : (m.ping && m.ping.reachable ? 'ping ok / ssh down' : 'down');
            }
        }

        // Update connection lines
        const lineMap = {
            'ryzen-strix-halo': 'kcs-line-ryzen-strix-halo',
            'ryzen-sligar': 'kcs-line-ryzen-sligar',
            'ryzen-minisforum': 'kcs-line-ryzen-minisforum',
            'strix-halo-sligar': 'kcs-line-strix-halo-sligar',
            'strix-halo-minisforum': 'kcs-line-strix-halo-minisforum',
            'sligar-minisforum': 'kcs-line-sligar-minisforum',
        };
        for (const conn of d.connections) {
            const key = conn.source + '-' + conn.target;
            const lineId = lineMap[key];
            if (lineId) {
                const line = document.getElementById(lineId);
                if (line) {
                    const up = conn.forward === 'up' && conn.reverse === 'up';
                    const partial = conn.forward === 'up' || conn.reverse === 'up';
                    line.setAttribute('stroke', up ? 'var(--green)' : partial ? 'var(--orange)' : 'var(--red)');
                    line.setAttribute('stroke-width', up ? '2' : '1');
                    line.setAttribute('stroke-dasharray', up ? '' : '4');
                }
            }
        }

        // Ring health summary
        const ringDot = document.getElementById('kcs-ring-dot');
        const ringLabel = document.getElementById('kcs-ring-label');
        const connCount = document.getElementById('kcs-conn-count');
        if (ringDot) ringDot.className = 'svc-dot ' + (d.ring_health === 'healthy' ? 'up' : d.ring_health === 'degraded' ? 'unknown' : 'down');
        if (ringLabel) ringLabel.textContent = d.ring_health;
        if (connCount) connCount.textContent = d.connections_up + '/' + d.connections_total + ' connections';
    } catch(e) {}
}

async function kcsTestAll() {
    const btn = event.target;
    btn.textContent = 'testing...';
    btn.disabled = true;
    try {
        await fetch('/cave/api/kcs/test-all', {method:'POST'});
        await kcsRefresh();
    } catch(e) {}
    btn.textContent = 'test all connections';
    btn.disabled = false;
}

async function kcsRepair(machine) {
    if (!confirm('Attempt SSH repair to ' + machine + '?')) return;
    try {
        const r = await fetch('/cave/api/kcs/repair/' + machine, {method:'POST'});
        const d = await r.json();
        alert(d.result.reachable ? machine + ' is back!' : 'Repair failed: ' + d.result.error);
        kcsRefresh();
    } catch(e) { alert('Error: ' + e); }
}

// Poll ring bus every 30s
kcsRefresh();
setInterval(kcsRefresh, 30000);


// ── ClusterFS — GlusterFS Status ────────────────────
async function kcsGlusterRefresh() {
    try {
        const r = await fetch('/cave/api/kcs/gluster');
        const d = await r.json();
        const dot = document.getElementById('kcs-fs-dot');
        const label = document.getElementById('kcs-fs-label');
        const pool = document.getElementById('kcs-fs-pool');

        if (dot) dot.className = 'svc-dot ' + (d.status === 'healthy' ? 'up' : d.status === 'degraded' ? 'unknown' : 'down');
        if (label) label.textContent = d.status;

        if (pool && d.pool_size && d.pool_size.total) {
            pool.textContent = d.pool_size.avail + ' free / ' + d.pool_size.total + ' total';
        } else if (pool) {
            pool.textContent = d.status === 'not installed' ? 'not installed' : '--';
        }
    } catch(e) {}
}

kcsGlusterRefresh();
setInterval(kcsGlusterRefresh, 30000);


// ── Halo Voice Indicator — Web Audio API ────────────
(function() {
    let audioCtx = null;
    let analyser = null;
    let stream = null;
    let animFrame = null;
    let active = false;

    const bars = document.querySelectorAll('.halo-bar');
    const indicator = document.getElementById('haloVoice');
    const statusLabel = document.getElementById('haloVoiceStatus');

    window.toggleHaloVoice = async function() {
        if (active) {
            // Stop listening
            active = false;
            if (animFrame) cancelAnimationFrame(animFrame);
            if (stream) stream.getTracks().forEach(t => t.stop());
            if (audioCtx) audioCtx.close();
            audioCtx = null;
            analyser = null;
            stream = null;
            indicator.classList.remove('active');
            statusLabel.textContent = 'click to listen';
            // Reset bars
            bars.forEach(bar => {
                bar.setAttribute('height', '8');
                bar.setAttribute('y', '-46');
                bar.style.opacity = '0.3';
            });
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioCtx = new AudioContext();
            const source = audioCtx.createMediaStreamSource(stream);
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 64;
            analyser.smoothingTimeConstant = 0.7;
            source.connect(analyser);

            active = true;
            indicator.classList.add('active');
            statusLabel.textContent = 'listening';
            animateVoice();
        } catch(e) {
            statusLabel.textContent = 'mic denied';
            setTimeout(() => { statusLabel.textContent = 'click to listen'; }, 2000);
        }
    };

    function animateVoice() {
        if (!active || !analyser) return;
        const data = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(data);

        // Map frequency bins to 12 bars
        const binCount = data.length;
        const step = Math.floor(binCount / 12);

        bars.forEach((bar, i) => {
            // Get average of a frequency range for this bar
            const start = i * step;
            let sum = 0;
            for (let j = start; j < start + step && j < binCount; j++) sum += data[j];
            const avg = sum / step;

            // Map 0-255 to bar height 4-22
            const h = 4 + (avg / 255) * 18;
            const y = -42 - h;

            bar.setAttribute('height', h.toFixed(1));
            bar.setAttribute('y', y.toFixed(1));
            bar.style.opacity = (0.3 + (avg / 255) * 0.7).toFixed(2);
        });

        animFrame = requestAnimationFrame(animateVoice);
    }
})();

// ── Halo Voice Dialog ──────────────
let haloDialogOpen = false;
let haloListening = false;

function openHaloDialog() {
    const dialog = document.getElementById('haloDialog');
    const orb = document.getElementById('haloVoice');
    const status = document.getElementById('haloVoiceStatus');
    
    if (haloDialogOpen) {
        closeHaloDialog();
        return;
    }

    haloDialogOpen = true;
    haloListening = true;
    orb.classList.add('active');
    orb.classList.add('listening');
    status.textContent = 'listening...';
    
    document.getElementById('haloUserText').textContent = '';
    document.getElementById('haloResponseText').textContent = 'listening...';
    dialog.classList.remove('fadeout');
    dialog.classList.add('show');

    // Start speech recognition if available
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = function(event) {
            let transcript = '';
            for (let i = 0; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            document.getElementById('haloUserText').textContent = '"' + transcript + '"';
            
            if (event.results[0].isFinal) {
                haloListening = false;
                orb.classList.remove('listening');
                status.textContent = 'thinking...';
                document.getElementById('haloResponseText').textContent = 'thinking...';
                sendToHalo(transcript);
            }
        };

        recognition.onerror = function() {
            haloListening = false;
            orb.classList.remove('listening');
            status.textContent = 'click to speak';
            document.getElementById('haloResponseText').textContent = 'could not hear you. try again.';
            setTimeout(closeHaloDialog, 3000);
        };

        recognition.onend = function() {
            if (haloListening) {
                // Timed out without speech
                haloListening = false;
                orb.classList.remove('listening');
                document.getElementById('haloResponseText').textContent = 'silence. click again when ready.';
                setTimeout(closeHaloDialog, 2500);
            }
        };

        recognition.start();
    } else {
        // No speech recognition — show text input
        document.getElementById('haloResponseText').innerHTML = '<input id="haloTextInput" type="text" placeholder="type your question..." style="background:transparent;border:1px solid rgba(0,136,255,0.3);border-radius:8px;padding:8px 12px;color:var(--text);width:100%;font-size:14px;outline:none;" onkeydown="if(event.key===\'Enter\'){sendToHalo(this.value);this.disabled=true;}">';
        setTimeout(() => document.getElementById('haloTextInput')?.focus(), 100);
    }
}

async function sendToHalo(text) {
    const status = document.getElementById('haloVoiceStatus');
    try {
        const resp = await fetch('/cave/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: text,
                agent: 'halo',
                system: 'You are Halo, the system orchestrator of halo-ai. Brief, authoritative, direct. One to three sentences max. Zero cloud. Zero data retention. You know every service and can direct users to them: Open WebUI (port 3000) for chat, ComfyUI (port 8188) for image gen, SearXNG (port 8888) for search, n8n (port 5678) for workflows, Whisper for speech-to-text, Kokoro for TTS, Qdrant for vector search, llama-server (port 8081) for inference at 87 tok/s. You know all 27 agents: Echo (social), Bounty (bugs), Meek (security), Amp (audio), Mechanic (hardware), Muse (entertainment), Sentinel (code), Forge (games), Dealer (game master), Conductor (composer), Quartermaster (servers), Crypto (arbitrage). When someone asks for a service, tell them exactly where to go. When they need an agent, route them by name.'
            })
        });
        const data = await resp.json();
        document.getElementById('haloResponseText').textContent = data.response || data.reply || 'I hear you.';
        status.textContent = 'halo';
    } catch (e) {
        document.getElementById('haloResponseText').textContent = 'Systems nominal. I hear you.';
        status.textContent = 'halo';
    }

    // Highlight relevant panels based on response
    const response = (data.response || data.reply || '').toLowerCase();
    const panelMap = {
        'lemonade': 'lemonade', 'llm': 'lemonade', 'inference': 'lemonade', 'tok/s': 'lemonade', 'model': 'lemonade',
        'stack': 'stack', 'freeze': 'stack', 'compile': 'stack', 'protection': 'stack', 'snapshot': 'stack',
        'agent': 'agents-detail', 'echo': 'agents-detail', 'bounty': 'agents-detail', 'meek': 'agents-detail',
        'amp': 'agents-detail', 'muse': 'agents-detail', 'mechanic': 'agents-detail', 'sentinel': 'agents-detail',
        'kansas': 'kcs', 'ssh': 'kcs', 'ring': 'kcs', 'mixer': 'kcs', 'mesh': 'kcs',
        'gluster': 'glusterfs', 'pool': 'glusterfs', 'replicate': 'glusterfs', 'storage': 'glusterfs',
        'activity': 'activity', 'news': 'news',
    };
    for (const [keyword, panelId] of Object.entries(panelMap)) {
        if (response.includes(keyword)) {
            const panel = document.querySelector(`[data-panel="${panelId}"]`);
            if (panel) {
                panel.style.transition = 'box-shadow 0.5s, border-color 0.5s';
                panel.style.boxShadow = '0 0 20px rgba(0,136,255,0.3)';
                panel.style.borderColor = 'rgba(0,136,255,0.5)';
                setTimeout(() => {
                    panel.style.boxShadow = '';
                    panel.style.borderColor = '';
                }, 6000);
                panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            break;
        }
    }

    // Fade out after 6 seconds
    setTimeout(closeHaloDialog, 6000);
}

function closeHaloDialog() {
    const dialog = document.getElementById('haloDialog');
    const orb = document.getElementById('haloVoice');
    const status = document.getElementById('haloVoiceStatus');
    
    dialog.classList.add('fadeout');
    orb.classList.remove('active');
    orb.classList.remove('listening');
    status.textContent = 'click to speak';
    
    setTimeout(() => {
        dialog.classList.remove('show');
        dialog.classList.remove('fadeout');
        haloDialogOpen = false;
    }, 500);
}

// Click outside dialog to close
document.addEventListener('click', function(e) {
    if (haloDialogOpen && !e.target.closest('#haloDialog') && !e.target.closest('#haloVoice')) {
        closeHaloDialog();
    }
});
