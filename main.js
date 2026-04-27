// ── Welcome overlay ──────────────────────────────────────────────────────────
function startApp() {
  const overlay = document.getElementById('welcomeOverlay');
  overlay.style.animation = 'fadeOutUp 0.4s ease forwards';
  setTimeout(() => overlay.classList.add('hidden'), 400);
}

// ── State ────────────────────────────────────────────────────────────────────
let activePolicyText = '';
let activeSummary = '';
let selectedScenarios = {};

// SCENARIO_DATA and DEFAULT_POLICY are injected from the template (index.html)

// ── Tabs ─────────────────────────────────────────────────────────────────────
function switchTab(name, evt) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  evt.currentTarget.classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
}

// ── File upload ──────────────────────────────────────────────────────────────
const zone = document.getElementById('uploadZone');
zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
zone.addEventListener('drop', e => {
  e.preventDefault(); zone.classList.remove('drag-over');
  if (e.dataTransfer.files[0]) processFile(e.dataTransfer.files[0]);
});

function handleFile(e) { if (e.target.files[0]) processFile(e.target.files[0]); }

async function processFile(file) {
  showStatus('uploadStatus', 'loading', `⏳ Extracting text from "${file.name}"...`);
  const fd = new FormData();
  fd.append('file', file);
  try {
    const r = await fetch('/api/extract-pdf', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.error) throw new Error(d.error);
    setPolicy(d.text);
    const backend = d.backend ? ` (via ${d.backend})` : '';
    showStatus('uploadStatus', 'success', `✓ Extracted ${d.chars.toLocaleString()} characters from "${file.name}"${backend}`);
  } catch (e) {
    const msg = e.message || 'Unknown error. Is the Flask server running?';
    showStatus('uploadStatus', 'error', `✕ ${msg}`);
  }
}

// ── Paste / Default ──────────────────────────────────────────────────────────
function usePasteText() {
  const t = document.getElementById('pasteText').value.trim();
  if (!t) { alert('Please paste some text first.'); return; }
  setPolicy(t);
}

function loadDefault() {
  setPolicy(DEFAULT_POLICY);
  showStatus('uploadStatus', 'success', '✓ Netflix Privacy Statement (Apr 2025) loaded successfully');
}

function setPolicy(text) {
  activePolicyText = text;
  document.getElementById('activeText').value = text;
  document.getElementById('activeChars').textContent = text.length.toLocaleString();
  document.getElementById('previewCard').style.display = 'block';
  document.getElementById('sumBtn').disabled = false;
}

// ── Summarisation ────────────────────────────────────────────────────────────
async function generateSummary() {
  if (!activePolicyText) { alert('No policy text loaded.'); return; }
  showStatus('sumStatus', 'loading', '🔍 Analysing privacy policy — this may take 20–40 seconds...');
  document.getElementById('sumBtn').disabled = true;
  updateSummaryStatus(false);
  try {
    const r = await fetch('/api/summarise', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ policy_text: activePolicyText })
    });
    const d = await r.json();
    if (d.error) throw new Error(d.error);
    activeSummary = d.summary;
    renderSummary(d.summary);
    showStatus('sumStatus', 'success', '✓ Summary generated — ready for scenario generation');
    updateSummaryStatus(true);
  } catch (e) {
    showStatus('sumStatus', 'error', `✕ ${e.message}`);
  } finally {
    document.getElementById('sumBtn').disabled = false;
  }
}

function renderSummary(text) {
  const card = document.getElementById('summaryCard');
  const out = document.getElementById('summaryOut');
  card.style.display = 'block';
  out.innerHTML = formatText(text);
}

function updateSummaryStatus(ready) {
  const el = document.getElementById('summaryStatus');
  const btn = document.getElementById('genBtn');
  if (ready && activeSummary) {
    el.innerHTML = `<span style="color:var(--success)">✓ Summary ready</span> — <span style="color:var(--text-muted);font-size:0.75rem">${activeSummary.length.toLocaleString()} chars · select scenarios below and generate drafts</span>`;
    el.style.fontStyle = 'normal';
    btn.disabled = false;
  } else {
    el.innerHTML = '⚠️ No summary yet — generate a summary in the left panel first.';
    el.style.fontStyle = 'italic';
    btn.disabled = true;
  }
}

// ── Scenario chips ────────────────────────────────────────────────────────────
function toggleChip(id) {
  const chip = document.getElementById('chip-' + id);
  if (selectedScenarios[id]) {
    delete selectedScenarios[id];
    chip.classList.remove('selected');
  } else {
    selectedScenarios[id] = SCENARIO_DATA[id];
    chip.classList.add('selected');
  }
}

// ── Generate scenarios ────────────────────────────────────────────────────────
async function generateScenarios() {
  if (!activeSummary) { alert('Please generate a policy summary first.'); return; }

  const list = [...Object.values(selectedScenarios)];
  const cName = document.getElementById('customName').value.trim();
  const cDesc = document.getElementById('customDesc').value.trim();
  if (cName && cDesc) {
    list.push({
      name: cName,
      description: cDesc,
      custom_requirements: document.getElementById('customReqs').value.trim()
    });
  }

  if (list.length === 0) {
    alert('Please select at least one scenario chip, or fill in a custom scenario name and description.');
    return;
  }

  showStatus('genStatus', 'loading', `⚡ Generating ${list.length} scenario draft(s) — please wait...`);
  document.getElementById('genBtn').disabled = true;
  document.getElementById('draftsContainer').innerHTML = '';

  let successCount = 0;
  for (const s of list) {
    const el = makePlaceholder(s.name);
    document.getElementById('draftsContainer').appendChild(el);
    try {
      const r = await fetch('/api/generate-scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          summary: activeSummary,
          scenario_name: s.name,
          scenario_description: s.description,
          custom_requirements: s.custom_requirements || ''
        })
      });
      const d = await r.json();
      if (d.error) throw new Error(d.error);
      fillDraft(el, s.name, d.draft);
      successCount++;
    } catch (e) {
      fillError(el, s.name, e.message);
    }
  }

  showStatus('genStatus', 'success', `✓ Generated ${successCount}/${list.length} scenario draft(s) — change selections to iterate`);
  document.getElementById('genBtn').disabled = false;
}

// ── Draft rendering helpers ──────────────────────────────────────────────────
function makePlaceholder(name) {
  const d = document.createElement('div');
  d.className = 'draft-card';
  d.innerHTML = `
    <div class="draft-header">
      <span class="draft-title">⏳ Generating: ${escHtml(name)}</span>
      <div class="spinner" style="border-top-color:var(--teal)"></div>
    </div>
    <div class="draft-body" style="color:var(--text-dim);font-style:italic">Drafting adapted policy...</div>`;
  return d;
}

function fillDraft(el, name, text) {
  el.innerHTML = `
    <div class="draft-header">
      <span class="draft-title">📜 ${escHtml(name)}</span>
      <button class="copy-btn" onclick="copyDraft(this)">Copy Draft</button>
    </div>
    <div class="draft-body">${formatText(text)}</div>`;
}

function fillError(el, name, msg) {
  el.innerHTML = `
    <div class="draft-header">
      <span class="draft-title" style="color:var(--error)">✕ Failed: ${escHtml(name)}</span>
    </div>
    <div class="draft-body" style="color:var(--error)">${escHtml(msg)}</div>`;
}

function clearDrafts() {
  document.getElementById('draftsContainer').innerHTML = `
    <div class="empty-state">
      <span class="icon">📜</span>
      <p>Adapted policy drafts will appear here.</p>
      <p style="font-size:.75rem;margin-top:.3rem">Select scenarios above and click <strong>Generate</strong>.</p>
      <p style="font-size:.72rem;margin-top:.5rem;color:var(--text-dim)">You can change scenarios and regenerate at any time.</p>
    </div>`;
  document.getElementById('genStatus').innerHTML = '';
}

// ── Text formatter ────────────────────────────────────────────────────────────
function formatText(t) {
  return t
    .replace(/^# (.+)$/gm, '<h2 style="font-size:1rem;color:var(--green-light);font-family:Playfair Display,serif;margin:.6rem 0 .25rem">$1</h2>')
    .replace(/^## (.+)$/gm, '<h2 style="color:var(--green-light);font-family:Playfair Display,serif;margin:.6rem 0 .25rem">$1</h2>')
    .replace(/^### (.+)$/gm, '<h3 style="color:var(--teal);font-family:JetBrains Mono,monospace;font-size:.82rem;margin:.4rem 0 .2rem">$1</h3>')
    .replace(/^---+$/gm, '<hr style="border:none;border-top:1px solid var(--border);margin:.5rem 0">')
    .replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--green-light)">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^[•\-] (.+)$/gm, '<li style="margin-left:1.2rem;margin-bottom:.2rem">$1</li>')
    .replace(/(<li.*<\/li>)/gs, '<ul style="margin:.3rem 0">$1</ul>')
    .replace(/\n/g, '<br>');
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Utilities ────────────────────────────────────────────────────────────────
function showStatus(id, type, msg) {
  const spin = type === 'loading' ? '<div class="spinner"></div>' : '';
  document.getElementById(id).innerHTML = `<div class="status ${type}">${spin}${msg}</div>`;
}

function copyEl(id) {
  const el = document.getElementById(id);
  navigator.clipboard.writeText(el.innerText || el.value)
    .then(() => alert('Copied to clipboard!'));
}

function copyDraft(btn) {
  const body = btn.closest('.draft-card').querySelector('.draft-body');
  navigator.clipboard.writeText(body.innerText)
    .then(() => { btn.textContent = '✓ Copied!'; setTimeout(() => btn.textContent = 'Copy Draft', 2000); });
}
