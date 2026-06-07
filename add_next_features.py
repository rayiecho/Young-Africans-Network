with open('yan-studio.html', 'r') as f:
    content = f.read()

# ── 1. VOICE SELECTION ──
old_voice_speed = '''          <div class="form-group">
            <label class="form-label">Voice Speed</label>
            <select id="voice-speed" class="form-select">
              <option value="0.85">Slow & Clear</option>
              <option value="0.95" selected>Normal</option>
              <option value="1.05">Slightly Fast</option>
            </select>
          </div>'''

new_voice_speed = '''          <div class="form-group">
            <label class="form-label">Voice</label>
            <select id="voice-select" class="form-select">
              <optgroup label="Female Voices">
                <option value="asteria">Asteria — Warm Female</option>
                <option value="athena">Athena — Clear Female</option>
                <option value="hera">Hera — Strong Female</option>
                <option value="luna">Luna — Soft Female</option>
                <option value="stella">Stella — Bright Female</option>
              </optgroup>
              <optgroup label="Male Voices">
                <option value="orion" selected>Orion — Deep Male</option>
                <option value="zeus">Zeus — Powerful Male</option>
                <option value="orpheus">Orpheus — Smooth Male</option>
                <option value="angus">Angus — Warm Male</option>
                <option value="arcas">Arcas — Clear Male</option>
                <option value="perseus">Perseus — Strong Male</option>
                <option value="helios">Helios — Energetic Male</option>
              </optgroup>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Voice Speed</label>
            <select id="voice-speed" class="form-select">
              <option value="0.85">Slow & Clear</option>
              <option value="0.95" selected>Normal</option>
              <option value="1.05">Slightly Fast</option>
            </select>
          </div>'''

content = content.replace(old_voice_speed, new_voice_speed, 1)

# Update TTS call to use voice-select
content = content.replace(
    "body: JSON.stringify({ text: scene.voiceover, voice: 'orion', speed: 1.1 })",
    "body: JSON.stringify({ text: scene.voiceover, voice: document.getElementById('voice-select').value })"
)

# ── 2. AUTO SUBTITLES WITH CLOUDFLARE WHISPER ──
old_auto_sub = "    } else if (subType === 'manual') {"
new_auto_sub = '''    } else if (subType === 'auto') {
      // Use Cloudflare Whisper for auto transcription
      addEnhanceLog('info', '🎤 Transcribing audio with AI...');
      try {
        const arrayBuffer = await enhanceVideo.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        const response = await fetch('https://yan-studio-worker.youngafricansn.workers.dev/transcribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/octet-stream' },
          body: uint8Array
        });
        const data = await response.json();
        if (data.text) {
          document.getElementById('manual-subtitle-text').value = data.text;
          document.getElementById('enhance-subtitles').value = 'manual';
          document.getElementById('manual-subtitle-card').style.display = 'block';
          addEnhanceLog('success', '✓ Auto-subtitles generated!');
        }
      } catch(e) {
        addEnhanceLog('error', '✗ Transcription failed: ' + e.message);
      }
    } else if (subType === 'manual') {'''

content = content.replace(old_auto_sub, new_auto_sub, 1)

# ── 3. VIDEO LIBRARY ──
# Add library tab
content = content.replace(
    '<button class="main-tab" id="tab-enhance" onclick="switchTab(\'enhance\')">✂️ Enhance Video</button>',
    '<button class="main-tab" id="tab-enhance" onclick="switchTab(\'enhance\')">✂️ Enhance Video</button>\n      <button class="main-tab" id="tab-library" onclick="switchTab(\'library\')">📚 Video Library</button>'
)

# Add library section
content = content.replace(
    "  </div><!-- end section-enhance -->",
    """  </div><!-- end section-enhance -->

  <!-- LIBRARY SECTION -->
  <div class="main-section" id="section-library">
    <div class="card">
      <div class="card-title"><div class="card-title-icon">📚</div>Your Video Library</div>
      <div id="library-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1rem;">
        <div style="text-align:center;color:var(--muted);padding:3rem;grid-column:span 3;font-family:var(--font-mono);font-size:0.82rem;">
          // No videos saved yet. Generate a video and save it to your library.
        </div>
      </div>
    </div>
  </div>"""
)

# Add library JS functions
content = content.replace(
    "function switchTab(tab) {",
    """// ── VIDEO LIBRARY ──
let videoLibrary = JSON.parse(localStorage.getItem('yan-video-library') || '[]');

function saveToLibrary(blob, title, duration) {
  const reader = new FileReader();
  reader.onload = function() {
    const entry = {
      id: Date.now(),
      title: title,
      duration: duration,
      date: new Date().toLocaleDateString(),
      size: (blob.size / 1024 / 1024).toFixed(1) + 'MB',
      data: reader.result
    };
    videoLibrary.unshift(entry);
    if (videoLibrary.length > 20) videoLibrary = videoLibrary.slice(0, 20);
    try { localStorage.setItem('yan-video-library', JSON.stringify(videoLibrary)); } catch(e) {}
    renderLibrary();
  };
  reader.readAsDataURL(blob);
}

function renderLibrary() {
  const grid = document.getElementById('library-grid');
  if (!videoLibrary.length) {
    grid.innerHTML = '<div style="text-align:center;color:var(--muted);padding:3rem;grid-column:span 3;font-family:var(--font-mono);font-size:0.82rem;">// No videos saved yet.</div>';
    return;
  }
  grid.innerHTML = videoLibrary.map(v => `
    <div style="background:var(--navy3);border:1px solid var(--border2);border-radius:12px;padding:1rem;">
      <div style="font-size:0.88rem;font-weight:700;margin-bottom:0.5rem;color:var(--white);">${v.title}</div>
      <div style="font-size:0.72rem;color:var(--muted);font-family:var(--font-mono);margin-bottom:1rem;">${v.date} · ${v.duration}s · ${v.size}</div>
      <div style="display:flex;gap:0.5rem;">
        <button onclick="downloadFromLibrary(${v.id})" style="flex:1;background:var(--gold);color:var(--navy);border:none;padding:0.5rem;border-radius:8px;font-size:0.78rem;font-weight:700;cursor:pointer;">⬇ Download</button>
        <button onclick="deleteFromLibrary(${v.id})" style="background:rgba(230,51,41,0.15);color:var(--red);border:1px solid rgba(230,51,41,0.3);padding:0.5rem 0.75rem;border-radius:8px;font-size:0.78rem;cursor:pointer;">🗑</button>
      </div>
    </div>
  `).join('');
}

function downloadFromLibrary(id) {
  const entry = videoLibrary.find(v => v.id === id);
  if (!entry) return;
  const a = document.createElement('a');
  a.href = entry.data;
  a.download = `YAN-${entry.title.replace(/[^a-z0-9]/gi,'-')}.webm`;
  a.click();
}

function deleteFromLibrary(id) {
  videoLibrary = videoLibrary.filter(v => v.id !== id);
  try { localStorage.setItem('yan-video-library', JSON.stringify(videoLibrary)); } catch(e) {}
  renderLibrary();
}

function switchTab(tab) {
  if (tab === 'library') renderLibrary();"""
)

# Update switchTab to handle library
content = content.replace(
    "  document.getElementById('section-create').classList.toggle('active', tab === 'create');\n  document.getElementById('section-enhance').classList.toggle('active', tab === 'enhance');\n  document.getElementById('tab-create').classList.toggle('active', tab === 'create');\n  document.getElementById('tab-enhance').classList.toggle('active', tab === 'enhance');",
    "  ['create','enhance','library'].forEach(t => {\n    document.getElementById('section-'+t).classList.toggle('active', t === tab);\n    document.getElementById('tab-'+t).classList.toggle('active', t === tab);\n  });"
)

# Auto-save to library after video generation
content = content.replace(
    "  addLog('success', '⬇ Video downloaded successfully!');",
    "  addLog('success', '⬇ Video downloaded successfully!');\n  saveToLibrary(videoBlob, scriptData.title, scriptData.duration);\n  addLog('success', '📚 Saved to Video Library!');"
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Voice selection + Auto subtitles + Video Library added!")
