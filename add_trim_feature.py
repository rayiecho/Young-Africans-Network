with open('yan-studio.html', 'r') as f:
    content = f.read()

# Add trim CSS
old_css = '  /* ENHANCER */'
new_css = '''  /* TRIM TIMELINE */
  .timeline-wrap { position:relative; height:60px; background:var(--navy3); border-radius:8px; overflow:hidden; cursor:pointer; margin:1rem 0; }
  .timeline-track { position:absolute; inset:0; display:flex; align-items:center; padding:0 8px; }
  .timeline-bar { flex:1; height:8px; background:rgba(245,166,35,0.2); border-radius:4px; position:relative; cursor:pointer; }
  .timeline-segment { position:absolute; top:0; height:100%; background:var(--gold); border-radius:4px; }
  .timeline-handle { position:absolute; top:50%; transform:translateY(-50%); width:14px; height:28px; background:var(--gold); border-radius:4px; cursor:ew-resize; z-index:2; }
  .timeline-handle.left { left:-7px; }
  .timeline-handle.right { right:-7px; }
  .clip-item { display:flex; align-items:center; gap:0.75rem; padding:0.65rem 1rem; background:var(--navy3); border-radius:8px; margin-bottom:0.5rem; border:1px solid var(--border2); }
  .clip-item .clip-time { font-family:var(--font-mono); font-size:0.78rem; color:var(--gold); }
  .clip-item .clip-remove { background:none; border:none; color:var(--red); cursor:pointer; font-size:1rem; margin-left:auto; }

  /* ENHANCER */'''

content = content.replace(old_css, new_css, 1)

# Add Trim & AI Edit card before the export card
old_export = '''      <!-- ACTIONS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">⚡</div>Export</div>'''

new_export = '''      <!-- TRIM & AI EDIT -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">✂️</div>Trim & AI Edit</div>
        
        <!-- AI INSTRUCTIONS -->
        <div class="form-group" style="margin-bottom:1.25rem;">
          <label class="form-label">AI Edit Instructions</label>
          <textarea id="ai-edit-instructions" class="form-textarea" style="min-height:80px;" placeholder="Type instructions in plain English:
- Keep only 1:30 to 4:00
- Remove the first 30 seconds
- Cut everything after 5 minutes
- Keep from 2:00 to 3:30 and 7:00 to 9:00"></textarea>
          <button onclick="applyAIEdit()" class="btn btn-gold" style="margin-top:0.75rem;padding:0.65rem 1.5rem;font-size:0.85rem;">🤖 Apply AI Edit</button>
        </div>

        <!-- MANUAL TIMELINE -->
        <div class="form-label" style="margin-bottom:0.5rem;">Manual Trim</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem;">
          <div class="form-group">
            <label class="form-label">Start Time</label>
            <input type="text" id="trim-start" class="form-input" placeholder="0:00" oninput="updateTrimPreview()">
          </div>
          <div class="form-group">
            <label class="form-label">End Time</label>
            <input type="text" id="trim-end" class="form-input" placeholder="0:30" oninput="updateTrimPreview()">
          </div>
        </div>
        
        <!-- TIMELINE VISUAL -->
        <div class="timeline-wrap" id="trim-timeline" onclick="seekToPosition(event)">
          <div class="timeline-track">
            <div class="timeline-bar" id="timeline-bar">
              <div class="timeline-segment" id="timeline-segment"></div>
              <div class="timeline-handle left" id="handle-left" onmousedown="startDrag('left', event)"></div>
              <div class="timeline-handle right" id="handle-right" onmousedown="startDrag('right', event)"></div>
            </div>
          </div>
          <div id="timeline-playhead" style="position:absolute;top:0;bottom:0;width:2px;background:#fff;left:0;pointer-events:none;"></div>
          <div id="timeline-time" style="position:absolute;bottom:4px;left:8px;font-size:0.68rem;font-family:var(--font-mono);color:var(--muted);">0:00 / 0:00</div>
        </div>

        <!-- CLIPS LIST -->
        <div id="clips-list" style="margin-top:1rem;"></div>
        
        <div class="btn-row" style="margin-top:1rem;">
          <button onclick="addClip()" class="btn btn-outline" style="font-size:0.85rem;">+ Add Clip</button>
          <button onclick="clearClips()" class="btn btn-outline" style="font-size:0.85rem;color:var(--red);border-color:var(--red);">✕ Clear All</button>
        </div>
      </div>

      <!-- ACTIONS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">⚡</div>Export</div>'''

content = content.replace(old_export, new_export, 1)

# Add trim & AI edit JS
old_wa_func = 'function shareEnhancedWhatsApp() {'
new_wa_func = '''// ── TRIM & AI EDIT ──
let clips = []; // [{start, end}]
let isDragging = false;
let dragHandle = null;
let trimStart = 0;
let trimEnd = 0;

function parseTime(str) {
  if (!str) return 0;
  const parts = str.split(':').map(Number);
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return parseFloat(str) || 0;
}

function formatTime(secs) {
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s.toString().padStart(2,'0')}`;
}

function updateTrimPreview() {
  const video = document.getElementById('original-video');
  if (!video.duration) return;
  const start = parseTime(document.getElementById('trim-start').value) || 0;
  const end = parseTime(document.getElementById('trim-end').value) || video.duration;
  trimStart = Math.max(0, Math.min(start, video.duration));
  trimEnd = Math.max(trimStart, Math.min(end, video.duration));
  updateTimeline();
}

function updateTimeline() {
  const video = document.getElementById('original-video');
  if (!video.duration) return;
  const dur = video.duration;
  const leftPct = (trimStart / dur) * 100;
  const rightPct = ((dur - trimEnd) / dur) * 100;
  const seg = document.getElementById('timeline-segment');
  const hl = document.getElementById('handle-left');
  const hr = document.getElementById('handle-right');
  if (seg) { seg.style.left = leftPct + '%'; seg.style.right = rightPct + '%'; }
  if (hl) hl.style.left = leftPct + '%';
  if (hr) hr.style.right = rightPct + '%';
  document.getElementById('timeline-time').textContent = `${formatTime(trimStart)} → ${formatTime(trimEnd)} / ${formatTime(dur)}`;
  document.getElementById('trim-start').value = formatTime(trimStart);
  document.getElementById('trim-end').value = formatTime(trimEnd);
}

function seekToPosition(e) {
  const video = document.getElementById('original-video');
  if (!video.duration) return;
  const bar = document.getElementById('trim-timeline');
  const rect = bar.getBoundingClientRect();
  const pct = (e.clientX - rect.left) / rect.width;
  video.currentTime = pct * video.duration;
}

function startDrag(handle, e) {
  isDragging = true;
  dragHandle = handle;
  e.preventDefault();
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag);
}

function onDrag(e) {
  if (!isDragging) return;
  const video = document.getElementById('original-video');
  if (!video.duration) return;
  const bar = document.getElementById('timeline-bar');
  const rect = bar.getBoundingClientRect();
  const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
  const time = pct * video.duration;
  if (dragHandle === 'left') { trimStart = Math.min(time, trimEnd - 1); }
  else { trimEnd = Math.max(time, trimStart + 1); }
  updateTimeline();
}

function stopDrag() {
  isDragging = false;
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
}

// Update playhead as video plays
setInterval(() => {
  const video = document.getElementById('original-video');
  const ph = document.getElementById('timeline-playhead');
  if (video && ph && video.duration) {
    ph.style.left = (video.currentTime / video.duration * 100) + '%';
  }
}, 100);

function addClip() {
  const video = document.getElementById('original-video');
  if (!video.duration) { alert('Upload a video first'); return; }
  const clip = { start: trimStart, end: trimEnd };
  clips.push(clip);
  renderClips();
  addEnhanceLog('success', `✓ Clip added: ${formatTime(clip.start)} → ${formatTime(clip.end)}`);
}

function renderClips() {
  const list = document.getElementById('clips-list');
  if (!clips.length) { list.innerHTML = ''; return; }
  list.innerHTML = `<div style="font-size:0.75rem;font-family:var(--font-mono);color:var(--gold);margin-bottom:0.5rem;">SELECTED CLIPS (${clips.length})</div>` +
    clips.map((c, i) => `
      <div class="clip-item">
        <span style="font-size:0.82rem;background:rgba(245,166,35,0.1);padding:0.2rem 0.6rem;border-radius:4px;font-family:var(--font-mono);color:var(--gold);">${i+1}</span>
        <span class="clip-time">${formatTime(c.start)} → ${formatTime(c.end)}</span>
        <span style="font-size:0.78rem;color:var(--muted);">(${formatTime(c.end - c.start)})</span>
        <button class="clip-remove" onclick="removeClip(${i})">✕</button>
      </div>
    `).join('');
}

function removeClip(i) {
  clips.splice(i, 1);
  renderClips();
}

function clearClips() {
  clips = [];
  renderClips();
  trimStart = 0;
  const video = document.getElementById('original-video');
  trimEnd = video.duration || 0;
  updateTimeline();
}

async function applyAIEdit() {
  const instructions = document.getElementById('ai-edit-instructions').value.trim();
  if (!instructions) { alert('Please type your edit instructions first.'); return; }
  const video = document.getElementById('original-video');
  if (!video.duration) { alert('Upload a video first.'); return; }

  addEnhanceLog('info', '🤖 AI is interpreting your instructions...');

  const prompt = `You are a video editor assistant. The video is ${formatTime(video.duration)} long (${Math.round(video.duration)} seconds total).

The user wants to edit this video with these instructions:
"${instructions}"

Return ONLY a JSON array of clips to KEEP (not remove). Each clip has start and end in seconds.
Example: [{"start": 90, "end": 240}, {"start": 420, "end": 540}]

Convert any time references like "1:30" to seconds (90). "Remove first 30 seconds" means start first clip at 30. "Keep only 2:00 to 4:00" means one clip from 120 to 240.

Return ONLY the JSON array, nothing else.`;

  try {
    const response = await fetch('https://yan-ai-worker.youngafricansn.workers.dev', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 500,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    const data = await response.json();
    const text = data.content[0].text.trim();
    const jsonMatch = text.match(/\\[[\\s\\S]*\\]/);
    if (!jsonMatch) throw new Error('No clips found');
    const aiClips = JSON.parse(jsonMatch[0]);
    clips = aiClips.map(c => ({
      start: Math.max(0, Math.min(c.start, video.duration)),
      end: Math.max(0, Math.min(c.end, video.duration))
    }));
    renderClips();
    if (clips.length > 0) {
      trimStart = clips[0].start;
      trimEnd = clips[0].end;
      updateTimeline();
    }
    addEnhanceLog('success', `✓ AI found ${clips.length} clip(s) to keep`);
  } catch(e) {
    addEnhanceLog('error', '✗ AI edit failed: ' + e.message);
  }
}

// Override startEnhancing to respect clips
const originalStartEnhancing = window.startEnhancing;

function shareEnhancedWhatsApp() {'''

content = content.replace(old_wa_func, new_wa_func, 1)

# Update startEnhancing to use clips if defined
old_render = '  // Play and render video\n  video.currentTime = 0;\n  video.play();\n  addEnhanceLog(\'success\', \'✓ Processing video frames...\');'

new_render = '''  // Use clips if defined, otherwise full video
  const useClips = clips && clips.length > 0;
  let clipIndex = 0;

  video.currentTime = useClips ? clips[0].start : 0;
  video.play();
  addEnhanceLog('success', useClips ? `✓ Processing ${clips.length} clip(s)...` : '✓ Processing video frames...');'''

content = content.replace(old_render, new_render, 1)

# Update renderFrame to handle clips
old_check_end = '''  video.addEventListener('ended', () => {
    if (enhanceMediaRecorder && enhanceMediaRecorder.state !== 'inactive') {
      enhanceMediaRecorder.stop();
    }
  });'''

new_check_end = '''  video.addEventListener('timeupdate', () => {
    if (clips && clips.length > 0 && clipIndex < clips.length) {
      const clip = clips[clipIndex];
      if (video.currentTime >= clip.end) {
        clipIndex++;
        if (clipIndex < clips.length) {
          video.currentTime = clips[clipIndex].start;
        } else {
          video.pause();
          if (enhanceMediaRecorder && enhanceMediaRecorder.state !== 'inactive') {
            enhanceMediaRecorder.stop();
          }
        }
      }
    }
  });

  video.addEventListener('ended', () => {
    if (enhanceMediaRecorder && enhanceMediaRecorder.state !== 'inactive') {
      enhanceMediaRecorder.stop();
    }
  });'''

content = content.replace(old_check_end, new_check_end, 1)

# Init timeline when video loads
old_video_load = '  video.onloadedmetadata = () => {'
new_video_load = '''  video.onloadedmetadata = () => {
    trimStart = 0;
    trimEnd = video.duration;
    clips = [];
    updateTimeline();'''

content = content.replace(old_video_load, new_video_load, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Trim & AI Edit added!")
