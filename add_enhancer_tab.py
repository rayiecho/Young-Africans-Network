with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add tab switcher CSS
old_css = '  /* MODE TOGGLE */'
new_css = '''  /* MAIN TABS */
  .main-tabs { display: flex; gap: 0; margin-bottom: 2rem; background: var(--navy2); border: 1px solid var(--border2); border-radius: 14px; overflow: hidden; }
  .main-tab { flex: 1; padding: 1rem 1.5rem; background: transparent; border: none; color: var(--muted); font-family: var(--font-display); font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
  .main-tab.active { background: rgba(245,166,35,0.1); color: var(--white); border-bottom: 2px solid var(--gold); }
  .main-tab:hover:not(.active) { background: rgba(245,166,35,0.05); color: var(--white); }
  .main-section { display: none; }
  .main-section.active { display: block; }

  /* ENHANCER */
  .upload-zone { border: 2px dashed var(--border); border-radius: 16px; padding: 3rem 2rem; text-align: center; cursor: pointer; transition: all 0.2s; background: var(--navy2); }
  .upload-zone:hover { border-color: var(--gold); background: rgba(245,166,35,0.05); }
  .upload-zone-icon { font-size: 3rem; margin-bottom: 1rem; }
  .upload-zone-text { font-size: 1rem; font-weight: 600; color: var(--white); margin-bottom: 0.5rem; }
  .upload-zone-sub { font-size: 0.82rem; color: var(--muted); font-family: var(--font-mono); }
  .enhance-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-top: 1.5rem; }
  .enhance-preview { width: 100%; border-radius: 12px; background: #000; aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; }
  .enhance-preview video { width: 100%; height: 100%; object-fit: contain; }
  .filter-slider { width: 100%; accent-color: var(--gold); margin-top: 0.5rem; }

  /* MODE TOGGLE */'''

content = content.replace(old_css, new_css, 1)

# 2. Add main tabs before steps-bar
old_steps = '    <!-- STEPS -->\n    <div class="steps-bar">'
new_steps = '''    <!-- MAIN TABS -->
    <div class="main-tabs">
      <button class="main-tab active" id="tab-create" onclick="switchTab('create')">🎬 Create Video</button>
      <button class="main-tab" id="tab-enhance" onclick="switchTab('enhance')">✂️ Enhance Video</button>
    </div>

    <!-- CREATE SECTION -->
    <div class="main-section active" id="section-create">

    <!-- STEPS -->
    <div class="steps-bar">'''

content = content.replace(old_steps, new_steps, 1)

# 3. Close create section before enhance section - find end of panels
old_end_panels = '  </div>\n</div>\n\n<script>'
new_end_panels = '''  </div>
  </div><!-- end section-create -->

  <!-- ENHANCE SECTION -->
  <div class="main-section" id="section-enhance">
    
    <!-- UPLOAD -->
    <div class="card" id="enhancer-upload-card">
      <div class="card-title">
        <div class="card-title-icon">📁</div>
        Upload Your Video
      </div>
      <div class="upload-zone" onclick="document.getElementById('video-file-input').click()" id="upload-zone">
        <input type="file" id="video-file-input" accept="video/*" style="display:none" onchange="loadVideoFile(event)">
        <div class="upload-zone-icon">🎥</div>
        <div class="upload-zone-text">Click to upload your video</div>
        <div class="upload-zone-sub">MP4, MOV, AVI, WebM supported</div>
      </div>
    </div>

    <!-- EDITOR (hidden until video loaded) -->
    <div id="enhancer-editor" style="display:none;">
      
      <!-- PREVIEW -->
      <div class="card">
        <div class="card-title">
          <div class="card-title-icon">👁</div>
          Preview
          <span class="tag tag-gold" id="enhance-filename">video.mp4</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
          <div>
            <div style="font-size:0.72rem;color:var(--muted);font-family:var(--font-mono);margin-bottom:0.5rem;">ORIGINAL</div>
            <div class="enhance-preview">
              <video id="original-video" controls></video>
            </div>
          </div>
          <div>
            <div style="font-size:0.72rem;color:var(--muted);font-family:var(--font-mono);margin-bottom:0.5rem;">ENHANCED PREVIEW</div>
            <div class="enhance-preview">
              <canvas id="enhance-canvas" style="width:100%;height:100%;"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- ADJUSTMENTS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">🎨</div>Visual Adjustments</div>
        <div class="enhance-grid">
          <div class="form-group">
            <label class="form-label">Brightness</label>
            <input type="range" class="filter-slider" id="adj-brightness" min="50" max="200" value="100" oninput="updatePreview()">
            <span class="form-hint" id="brightness-val">100%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Contrast</label>
            <input type="range" class="filter-slider" id="adj-contrast" min="50" max="200" value="100" oninput="updatePreview()">
            <span class="form-hint" id="contrast-val">100%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Saturation</label>
            <input type="range" class="filter-slider" id="adj-saturation" min="0" max="200" value="100" oninput="updatePreview()">
            <span class="form-hint" id="saturation-val">100%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Sharpness</label>
            <input type="range" class="filter-slider" id="adj-sharpness" min="0" max="5" value="0" step="0.5" oninput="updatePreview()">
            <span class="form-hint" id="sharpness-val">0</span>
          </div>
        </div>
      </div>

      <!-- ENHANCEMENTS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">✨</div>Enhancements</div>
        <div class="enhance-grid">
          <div class="form-group">
            <label class="form-label">Add Subtitles</label>
            <select id="enhance-subtitles" class="form-select">
              <option value="none">No Subtitles</option>
              <option value="auto">Auto Generate (AI)</option>
              <option value="manual">Manual Text</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Background Music</label>
            <select id="enhance-music" class="form-select">
              <option value="none">No Music</option>
              <option value="inspirational">🌍 Inspirational</option>
              <option value="upbeat">⚡ Upbeat</option>
              <option value="calm">🌊 Calm</option>
              <option value="corporate">💼 Corporate</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">YAN Intro</label>
            <select id="enhance-intro" class="form-select">
              <option value="none">No Intro</option>
              <option value="yan">YAN Branded Intro (3s)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">YAN Outro</label>
            <select id="enhance-outro" class="form-select">
              <option value="none">No Outro</option>
              <option value="yan">YAN Branded Outro (3s)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Watermark</label>
            <select id="enhance-watermark" class="form-select">
              <option value="none">No Watermark</option>
              <option value="yan-tl">YAN Logo — Top Left</option>
              <option value="yan-tr">YAN Logo — Top Right</option>
              <option value="yan-br">YAN Logo — Bottom Right</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Video Filter</label>
            <select id="enhance-filter" class="form-select" onchange="updatePreview()">
              <option value="none">None</option>
              <option value="vivid">🌈 Vivid</option>
              <option value="warm">🌅 Warm</option>
              <option value="cool">❄️ Cool</option>
              <option value="bw">⚫ Black & White</option>
              <option value="cinematic">🎬 Cinematic</option>
            </select>
          </div>
        </div>
      </div>

      <!-- MANUAL SUBTITLE TEXT -->
      <div class="card" id="manual-subtitle-card" style="display:none;">
        <div class="card-title"><div class="card-title-icon">💬</div>Subtitle Text</div>
        <div class="form-group">
          <label class="form-label">Enter Subtitles</label>
          <textarea id="manual-subtitle-text" class="form-textarea" placeholder="Type your subtitle text here. It will appear at the bottom of the video throughout."></textarea>
        </div>
      </div>

      <!-- ACTIONS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">⚡</div>Export</div>
        <div class="btn-row">
          <button class="btn btn-gold" onclick="startEnhancing()">✨ Enhance & Export</button>
          <button class="btn btn-outline" onclick="resetEnhancer()">↺ Reset</button>
        </div>
        <div class="status-log" id="enhance-log" style="margin-top:1rem;">
          <span class="log-line info">// Upload a video to get started.</span>
        </div>
        <div class="progress-wrap" id="enhance-progress" style="display:none;margin-top:1rem;">
          <div class="progress-label">
            <span id="enhance-progress-label">Processing...</span>
            <span id="enhance-progress-pct">0%</span>
          </div>
          <div class="progress-bar"><div class="progress-fill" id="enhance-progress-fill"></div></div>
        </div>
      </div>

    </div><!-- end enhancer-editor -->
  </div><!-- end section-enhance -->

</div>

<script>'''

content = content.replace(old_end_panels, new_end_panels, 1)

# 4. Add tab switching + enhancer JS before closing script
old_end_script = 'function makeAnother() {'
new_end_script = '''// ── TAB SWITCHING ──
function switchTab(tab) {
  document.getElementById('section-create').classList.toggle('active', tab === 'create');
  document.getElementById('section-enhance').classList.toggle('active', tab === 'enhance');
  document.getElementById('tab-create').classList.toggle('active', tab === 'create');
  document.getElementById('tab-enhance').classList.toggle('active', tab === 'enhance');
}

// ── ENHANCER ──
let enhanceVideo = null;
let enhanceRecordedChunks = [];
let enhanceMediaRecorder = null;

function loadVideoFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  enhanceVideo = file;
  const url = URL.createObjectURL(file);
  const video = document.getElementById('original-video');
  video.src = url;
  video.load();
  document.getElementById('enhance-filename').textContent = file.name;
  document.getElementById('enhancer-editor').style.display = 'block';
  document.getElementById('enhancer-upload-card').style.display = 'none';
  addEnhanceLog('success', `✓ Loaded: ${file.name}`);
  
  video.onloadedmetadata = () => {
    const canvas = document.getElementById('enhance-canvas');
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    updatePreview();
  };
}

function getFilterCSS() {
  const b = document.getElementById('adj-brightness').value;
  const c = document.getElementById('adj-contrast').value;
  const s = document.getElementById('adj-saturation').value;
  const filter = document.getElementById('enhance-filter').value;
  
  document.getElementById('brightness-val').textContent = b + '%';
  document.getElementById('contrast-val').textContent = c + '%';
  document.getElementById('saturation-val').textContent = s + '%';
  document.getElementById('sharpness-val').textContent = document.getElementById('adj-sharpness').value;
  
  let filterStr = `brightness(${b}%) contrast(${c}%) saturate(${s}%)`;
  if (filter === 'vivid') filterStr += ' saturate(150%) contrast(110%)';
  if (filter === 'warm') filterStr += ' sepia(30%) saturate(120%)';
  if (filter === 'cool') filterStr += ' hue-rotate(20deg) saturate(80%)';
  if (filter === 'bw') filterStr += ' grayscale(100%)';
  if (filter === 'cinematic') filterStr += ' contrast(120%) saturate(80%) brightness(90%)';
  
  return filterStr;
}

function updatePreview() {
  const video = document.getElementById('original-video');
  const canvas = document.getElementById('enhance-canvas');
  const ctx = canvas.getContext('2d');
  
  if (!video.src) return;
  
  ctx.filter = getFilterCSS();
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  ctx.filter = 'none';
  
  // Watermark
  const wm = document.getElementById('enhance-watermark').value;
  if (wm !== 'none') {
    ctx.fillStyle = 'rgba(245,166,35,0.8)';
    ctx.font = 'bold 14px Syne, sans-serif';
    ctx.textAlign = wm.includes('r') ? 'right' : 'left';
    const x = wm.includes('r') ? canvas.width - 16 : 16;
    const y = wm.includes('t') ? 30 : canvas.height - 16;
    ctx.fillText('YAN', x, y);
  }
  
  // Subtitles
  const subType = document.getElementById('enhance-subtitles').value;
  document.getElementById('manual-subtitle-card').style.display = subType === 'manual' ? 'block' : 'none';
  
  if (subType === 'manual') {
    const text = document.getElementById('manual-subtitle-text').value;
    if (text) {
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.fillRect(0, canvas.height - 60, canvas.width, 60);
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 22px Syne, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(text.split('\\n')[0], canvas.width/2, canvas.height - 24);
    }
  }
}

// Live preview as video plays
document.addEventListener('DOMContentLoaded', () => {
  const video = document.getElementById('original-video');
  if (video) {
    video.addEventListener('timeupdate', updatePreview);
    video.addEventListener('play', function previewLoop() {
      if (!video.paused) {
        updatePreview();
        requestAnimationFrame(previewLoop);
      }
    });
  }
});

async function startEnhancing() {
  if (!enhanceVideo) { alert('Please upload a video first.'); return; }
  
  addEnhanceLog('info', '▶ Starting enhancement...');
  document.getElementById('enhance-progress').style.display = 'block';
  
  const video = document.getElementById('original-video');
  const canvas = document.getElementById('enhance-canvas');
  canvas.width = video.videoWidth || 1280;
  canvas.height = video.videoHeight || 720;
  
  // Setup AudioContext for music
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const dest = audioCtx.createMediaStreamDestination();
  
  // Capture canvas stream
  const canvasStream = canvas.captureStream(30);
  canvasStream.addTrack(dest.stream.getAudioTracks()[0]);
  
  // Add original video audio
  const videoSource = audioCtx.createMediaElementSource(video);
  videoSource.connect(dest);
  videoSource.connect(audioCtx.destination);
  
  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus') 
    ? 'video/webm;codecs=vp9,opus' : 'video/webm';
  
  enhanceRecordedChunks = [];
  enhanceMediaRecorder = new MediaRecorder(canvasStream, { mimeType, videoBitsPerSecond: 3000000 });
  enhanceMediaRecorder.ondataavailable = e => { if (e.data.size > 0) enhanceRecordedChunks.push(e.data); };
  enhanceMediaRecorder.onstop = finishEnhancing;
  enhanceMediaRecorder.start(100);
  
  // Start background music
  const musicType = document.getElementById('enhance-music').value;
  if (musicType !== 'none') {
    startBackgroundMusic(audioCtx, dest, musicType, video.duration || 60);
    addEnhanceLog('success', '✓ Background music added');
  }
  
  // Play and render video
  video.currentTime = 0;
  video.play();
  addEnhanceLog('success', '✓ Processing video frames...');
  
  function renderFrame() {
    if (video.paused || video.ended) {
      enhanceMediaRecorder.stop();
      return;
    }
    
    const progress = video.currentTime / video.duration;
    document.getElementById('enhance-progress-fill').style.width = (progress * 100) + '%';
    document.getElementById('enhance-progress-pct').textContent = Math.round(progress * 100) + '%';
    document.getElementById('enhance-progress-label').textContent = `Processing frame ${Math.round(video.currentTime)}s / ${Math.round(video.duration)}s`;
    
    // Draw filtered frame
    const ctx = canvas.getContext('2d');
    ctx.filter = getFilterCSS();
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    ctx.filter = 'none';
    
    // Watermark
    const wm = document.getElementById('enhance-watermark').value;
    if (wm !== 'none') {
      ctx.fillStyle = 'rgba(245,166,35,0.85)';
      ctx.font = 'bold 18px Syne, sans-serif';
      ctx.textAlign = wm.includes('r') ? 'right' : 'left';
      const x = wm.includes('r') ? canvas.width - 20 : 20;
      const y = wm.includes('t') ? 36 : canvas.height - 20;
      ctx.fillText('YAN', x, y);
    }
    
    // Subtitles
    const subType = document.getElementById('enhance-subtitles').value;
    if (subType === 'manual') {
      const text = document.getElementById('manual-subtitle-text').value;
      if (text) {
        const lines = text.split('\\n');
        const lineIdx = Math.floor((video.currentTime / video.duration) * lines.length);
        const currentLine = lines[Math.min(lineIdx, lines.length - 1)];
        ctx.fillStyle = 'rgba(0,0,0,0.65)';
        ctx.fillRect(0, canvas.height - 64, canvas.width, 64);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 24px Syne, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(currentLine, canvas.width/2, canvas.height - 22);
      }
    }
    
    requestAnimationFrame(renderFrame);
  }
  
  video.addEventListener('ended', () => {
    if (enhanceMediaRecorder && enhanceMediaRecorder.state !== 'inactive') {
      enhanceMediaRecorder.stop();
    }
  });
  
  renderFrame();
}

function finishEnhancing() {
  const blob = new Blob(enhanceRecordedChunks, { type: 'video/webm' });
  const sizeMB = (blob.size / 1024 / 1024).toFixed(1);
  addEnhanceLog('success', `✓ Enhanced video ready! Size: ${sizeMB}MB`);
  
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `YAN-Enhanced-${Date.now()}.webm`;
  a.click();
  URL.revokeObjectURL(url);
  
  document.getElementById('enhance-progress-label').textContent = 'Done!';
  document.getElementById('enhance-progress-pct').textContent = '100%';
  document.getElementById('enhance-progress-fill').style.width = '100%';
}

function addEnhanceLog(type, msg) {
  const log = document.getElementById('enhance-log');
  const line = document.createElement('span');
  line.className = `log-line ${type}`;
  line.textContent = msg;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

function resetEnhancer() {
  enhanceVideo = null;
  document.getElementById('enhancer-editor').style.display = 'none';
  document.getElementById('enhancer-upload-card').style.display = 'block';
  document.getElementById('video-file-input').value = '';
  document.getElementById('enhance-log').innerHTML = '<span class="log-line info">// Upload a video to get started.</span>';
}

function makeAnother() {'''

content = content.replace(old_end_script, new_end_script, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Enhance Video tab added!")
