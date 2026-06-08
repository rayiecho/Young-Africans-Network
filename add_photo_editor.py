with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add Photo Editor tab button
old_tabs = '<button class="main-tab" id="tab-library" onclick="switchTab(\'library\')">📚 Video Library</button>'
new_tabs = '''<button class="main-tab" id="tab-library" onclick="switchTab('library')">📚 Video Library</button>
      <button class="main-tab" id="tab-photo" onclick="switchTab('photo')">🖼 Photo Editor</button>'''

content = content.replace(old_tabs, new_tabs, 1)

# 2. Update switchTab to handle photo
old_switch = "  ['create','enhance','library'].forEach(t => {"
new_switch = "  ['create','enhance','library','photo'].forEach(t => {"
content = content.replace(old_switch, new_switch, 1)

# 3. Add photo editor section before closing main div
old_end = "  </div><!-- end section-enhance -->"
new_end = """  </div><!-- end section-enhance -->

  <!-- PHOTO EDITOR SECTION -->
  <div class="main-section" id="section-photo">

    <!-- UPLOAD -->
    <div class="card" id="photo-upload-card">
      <div class="card-title"><div class="card-title-icon">🖼</div>Photo Editor</div>
      <div class="upload-zone" onclick="document.getElementById('photo-file-input').click()">
        <input type="file" id="photo-file-input" accept="image/*" style="display:none" onchange="loadPhotoFile(event)">
        <div class="upload-zone-icon">🖼</div>
        <div class="upload-zone-text">Click to upload your photo</div>
        <div class="upload-zone-sub">JPG, PNG, WEBP supported</div>
      </div>
    </div>

    <!-- EDITOR -->
    <div id="photo-editor" style="display:none;">

      <!-- PREVIEW -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">👁</div>Preview
          <span class="tag tag-gold" id="photo-filename">photo.jpg</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
          <div>
            <div style="font-size:0.72rem;color:var(--muted);font-family:var(--font-mono);margin-bottom:0.5rem;">ORIGINAL</div>
            <div style="border-radius:12px;overflow:hidden;background:#000;max-height:300px;display:flex;align-items:center;justify-content:center;">
              <img id="original-photo" style="max-width:100%;max-height:300px;object-fit:contain;">
            </div>
          </div>
          <div>
            <div style="font-size:0.72rem;color:var(--muted);font-family:var(--font-mono);margin-bottom:0.5rem;">EDITED</div>
            <div style="border-radius:12px;overflow:hidden;background:#000;max-height:300px;display:flex;align-items:center;justify-content:center;">
              <canvas id="photo-canvas" style="max-width:100%;max-height:300px;object-fit:contain;"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- AI INSTRUCTIONS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">🤖</div>AI Edit Instructions</div>
        <div class="form-group">
          <textarea id="photo-ai-instructions" class="form-textarea" style="min-height:80px;" placeholder="Type what you want:
- Make it look professional
- Brighten it up
- Make it look like iPhone photo
- Add warm filter
- Make it black and white
- Sharpen and enhance quality
- Add YAN watermark"></textarea>
          <button onclick="applyPhotoAIEdit()" class="btn btn-gold" style="margin-top:0.75rem;padding:0.65rem 1.5rem;font-size:0.85rem;">🤖 Apply AI Edit</button>
        </div>
      </div>

      <!-- QUALITY PRESETS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">✨</div>Quick Presets</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;">
          <button onclick="applyPhotoPreset('iphone')" class="preset-btn">📱 iPhone</button>
          <button onclick="applyPhotoPreset('dslr')" class="preset-btn">📷 DSLR</button>
          <button onclick="applyPhotoPreset('cinema')" class="preset-btn">🎬 Cinema</button>
          <button onclick="applyPhotoPreset('portrait')" class="preset-btn">👤 Portrait</button>
          <button onclick="applyPhotoPreset('vivid')" class="preset-btn">🌈 Vivid</button>
          <button onclick="applyPhotoPreset('bw')" class="preset-btn">⚫ B&W</button>
          <button onclick="applyPhotoPreset('warm')" class="preset-btn">🌅 Warm</button>
          <button onclick="applyPhotoPreset('cool')" class="preset-btn">❄️ Cool</button>
          <button onclick="applyPhotoPreset('reset')" class="preset-btn" style="color:var(--muted);">↺ Reset</button>
        </div>
      </div>

      <!-- MANUAL ADJUSTMENTS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">🎨</div>Manual Adjustments</div>
        <div class="enhance-grid">
          <div class="form-group">
            <label class="form-label">Brightness</label>
            <input type="range" class="filter-slider" id="photo-brightness" min="0" max="300" value="100" oninput="updatePhotoPreview();document.getElementById('pb-val').textContent=this.value+'%'">
            <span class="form-hint" id="pb-val">100%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Contrast</label>
            <input type="range" class="filter-slider" id="photo-contrast" min="0" max="300" value="100" oninput="updatePhotoPreview();document.getElementById('pc-val').textContent=this.value+'%'">
            <span class="form-hint" id="pc-val">100%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Saturation</label>
            <input type="range" class="filter-slider" id="photo-saturation" min="0" max="300" value="100" oninput="updatePhotoPreview();document.getElementById('ps-val').textContent=this.value+'%'">
            <span class="form-hint" id="ps-val">100%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Sharpness</label>
            <input type="range" class="filter-slider" id="photo-sharpness" min="0" max="10" value="0" step="0.5" oninput="updatePhotoPreview();document.getElementById('psh-val').textContent=this.value">
            <span class="form-hint" id="psh-val">0</span>
          </div>
          <div class="form-group">
            <label class="form-label">Warmth</label>
            <input type="range" class="filter-slider" id="photo-warmth" min="-100" max="100" value="0" oninput="updatePhotoPreview();document.getElementById('pw-val').textContent=this.value">
            <span class="form-hint" id="pw-val">0</span>
          </div>
          <div class="form-group">
            <label class="form-label">Rotate</label>
            <input type="range" class="filter-slider" id="photo-rotate" min="-180" max="180" value="0" oninput="updatePhotoPreview();document.getElementById('pr-val').textContent=this.value+'°'">
            <span class="form-hint" id="pr-val">0°</span>
          </div>
        </div>
      </div>

      <!-- TEXT OVERLAY -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">💬</div>Text & Watermark</div>
        <div class="enhance-grid">
          <div class="form-group full">
            <label class="form-label">Add Text</label>
            <input type="text" id="photo-text" class="form-input" placeholder="e.g. Young Africans Network" oninput="updatePhotoPreview()">
          </div>
          <div class="form-group">
            <label class="form-label">Text Position</label>
            <select id="photo-text-pos" class="form-select" onchange="updatePhotoPreview()">
              <option value="none">No Text</option>
              <option value="bottom">Bottom Center</option>
              <option value="top">Top Center</option>
              <option value="br">Bottom Right</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">YAN Watermark</label>
            <select id="photo-watermark" class="form-select" onchange="updatePhotoPreview()">
              <option value="none">No Watermark</option>
              <option value="br">YAN — Bottom Right</option>
              <option value="bl">YAN — Bottom Left</option>
              <option value="tr">YAN — Top Right</option>
            </select>
          </div>
        </div>
      </div>

      <!-- EXPORT -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">⚡</div>Download</div>
        <div class="form-group" style="margin-bottom:1rem;">
          <label class="form-label">Format</label>
          <select id="photo-format" class="form-select">
            <option value="jpeg">JPEG (smaller file)</option>
            <option value="png">PNG (better quality)</option>
            <option value="webp">WebP (best compression)</option>
          </select>
        </div>
        <div class="btn-row">
          <button onclick="downloadPhoto()" class="btn btn-green">⬇ Download Photo</button>
          <button onclick="resetPhotoEditor()" class="btn btn-outline">↺ Reset</button>
        </div>
        <div class="status-log" id="photo-log" style="margin-top:1rem;">
          <span class="log-line info">// Upload a photo to get started.</span>
        </div>
      </div>

    </div><!-- end photo-editor -->
  </div><!-- end section-photo -->"""

content = content.replace(old_end, new_end, 1)

# 4. Add preset-btn CSS
old_css_end = '  /* RESPONSIVE */'
new_css_end = '''  .preset-btn { background:var(--navy3); border:1px solid var(--border); color:var(--white); padding:0.75rem; border-radius:8px; font-size:0.8rem; font-weight:600; cursor:pointer; transition:all 0.2s; }
  .preset-btn:hover { border-color:var(--gold); color:var(--gold); }

  /* RESPONSIVE */'''
content = content.replace(old_css_end, new_css_end, 1)

# 5. Add photo editor JS
old_make_another = 'function makeAnother() {'
new_make_another = '''// ── PHOTO EDITOR ──
let photoImage = null;

function loadPhotoFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  const img = new Image();
  img.onload = () => {
    photoImage = img;
    document.getElementById('original-photo').src = url;
    document.getElementById('photo-filename').textContent = file.name;
    const canvas = document.getElementById('photo-canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    document.getElementById('photo-upload-card').style.display = 'none';
    document.getElementById('photo-editor').style.display = 'block';
    updatePhotoPreview();
    addPhotoLog('success', `✓ Loaded: ${file.name} (${img.width}x${img.height})`);
  };
  img.src = url;
}

function getPhotoFilter() {
  const b = document.getElementById('photo-brightness').value;
  const c = document.getElementById('photo-contrast').value;
  const s = document.getElementById('photo-saturation').value;
  const sh = parseFloat(document.getElementById('photo-sharpness').value);
  const w = parseInt(document.getElementById('photo-warmth').value);
  let f = `brightness(${b}%) contrast(${c}%) saturate(${s}%)`;
  if (sh > 0) f += ` contrast(${100 + sh * 6}%)`;
  if (w > 0) f += ` sepia(${w * 0.4}%) saturate(${100 + w * 0.3}%)`;
  if (w < 0) f += ` hue-rotate(${w * 0.2}deg) saturate(${100 + w * 0.3}%)`;
  return f;
}

function updatePhotoPreview() {
  if (!photoImage) return;
  const canvas = document.getElementById('photo-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const rotate = parseInt(document.getElementById('photo-rotate').value) * Math.PI / 180;

  ctx.clearRect(0, 0, W, H);
  ctx.save();
  ctx.translate(W/2, H/2);
  ctx.rotate(rotate);
  ctx.filter = getPhotoFilter();
  ctx.drawImage(photoImage, -W/2, -H/2, W, H);
  ctx.filter = 'none';
  ctx.restore();

  // Watermark
  const wm = document.getElementById('photo-watermark').value;
  if (wm !== 'none') {
    ctx.fillStyle = 'rgba(245,166,35,0.85)';
    ctx.font = `bold ${Math.round(W * 0.035)}px Syne, sans-serif`;
    ctx.textAlign = wm.includes('r') ? 'right' : 'left';
    const x = wm.includes('r') ? W - 16 : 16;
    const y = wm.includes('t') ? 36 : H - 16;
    ctx.fillText('YAN | youngafricansnetwork.org', x, y);
  }

  // Text overlay
  const textPos = document.getElementById('photo-text-pos').value;
  const text = document.getElementById('photo-text').value;
  if (textPos !== 'none' && text) {
    const fontSize = Math.round(W * 0.04);
    ctx.font = `bold ${fontSize}px Syne, sans-serif`;
    ctx.textAlign = textPos === 'br' ? 'right' : 'center';
    const x = textPos === 'br' ? W - 20 : W/2;
    const y = textPos === 'top' ? fontSize + 20 : H - 24;
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(0, y - fontSize - 8, W, fontSize + 20);
    ctx.fillStyle = '#ffffff';
    ctx.fillText(text, x, y);
  }
}

function applyPhotoPreset(preset) {
  const presets = {
    iphone:   { b:108, c:115, s:125, sh:2.5, w:15 },
    dslr:     { b:102, c:120, s:110, sh:3.5, w:0  },
    cinema:   { b:95,  c:130, s:75,  sh:2,   w:-10 },
    portrait: { b:110, c:108, s:105, sh:1.5, w:10 },
    vivid:    { b:105, c:115, s:160, sh:2,   w:5  },
    bw:       { b:105, c:115, s:0,   sh:2,   w:0  },
    warm:     { b:105, c:110, s:115, sh:1,   w:60 },
    cool:     { b:100, c:110, s:90,  sh:1,   w:-50 },
    reset:    { b:100, c:100, s:100, sh:0,   w:0  }
  };
  const p = presets[preset];
  if (!p) return;
  document.getElementById('photo-brightness').value = p.b;
  document.getElementById('photo-contrast').value = p.c;
  document.getElementById('photo-saturation').value = p.s;
  document.getElementById('photo-sharpness').value = p.sh;
  document.getElementById('photo-warmth').value = p.w;
  document.getElementById('pb-val').textContent = p.b + '%';
  document.getElementById('pc-val').textContent = p.c + '%';
  document.getElementById('ps-val').textContent = p.s + '%';
  document.getElementById('psh-val').textContent = p.sh;
  document.getElementById('pw-val').textContent = p.w;
  updatePhotoPreview();
  addPhotoLog('success', `✓ ${preset} preset applied`);
}

async function applyPhotoAIEdit() {
  const instructions = document.getElementById('photo-ai-instructions').value.trim();
  if (!instructions) { alert('Type your instructions first'); return; }
  addPhotoLog('info', '🤖 AI interpreting instructions...');

  const prompt = `You are a photo editor assistant. The user wants to edit their photo with these instructions: "${instructions}"

Return ONLY a JSON object with these exact fields (numbers only):
{
  "brightness": 100,
  "contrast": 100,
  "saturation": 100,
  "sharpness": 0,
  "warmth": 0,
  "watermark": "none",
  "text": "",
  "textPos": "none"
}

brightness: 0-300 (100=normal, 150=bright)
contrast: 0-300 (100=normal, 130=more contrast)
saturation: 0-300 (100=normal, 0=black&white)
sharpness: 0-10 (0=normal, 5=sharp)
warmth: -100 to 100 (negative=cool, positive=warm)
watermark: "none", "br", "bl", "tr"
text: any text to add or empty string
textPos: "none", "bottom", "top", "br"`;

  try {
    const response = await fetch('https://yan-ai-worker.youngafricansn.workers.dev', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 300,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    const data = await response.json();
    const text = data.content[0].text.trim();
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error('No JSON');
    const p = JSON.parse(jsonMatch[0]);

    document.getElementById('photo-brightness').value = p.brightness || 100;
    document.getElementById('photo-contrast').value = p.contrast || 100;
    document.getElementById('photo-saturation').value = p.saturation || 100;
    document.getElementById('photo-sharpness').value = p.sharpness || 0;
    document.getElementById('photo-warmth').value = p.warmth || 0;
    document.getElementById('pb-val').textContent = (p.brightness||100) + '%';
    document.getElementById('pc-val').textContent = (p.contrast||100) + '%';
    document.getElementById('ps-val').textContent = (p.saturation||100) + '%';
    document.getElementById('psh-val').textContent = p.sharpness || 0;
    document.getElementById('pw-val').textContent = p.warmth || 0;
    if (p.watermark) document.getElementById('photo-watermark').value = p.watermark;
    if (p.text) document.getElementById('photo-text').value = p.text;
    if (p.textPos) document.getElementById('photo-text-pos').value = p.textPos;

    updatePhotoPreview();
    addPhotoLog('success', '✓ AI edit applied!');
  } catch(e) {
    addPhotoLog('error', '✗ AI edit failed: ' + e.message);
  }
}

function downloadPhoto() {
  const canvas = document.getElementById('photo-canvas');
  const format = document.getElementById('photo-format').value;
  const quality = format === 'jpeg' ? 0.92 : 1;
  const url = canvas.toDataURL(`image/${format}`, quality);
  const a = document.createElement('a');
  a.href = url;
  a.download = `YAN-Photo-${Date.now()}.${format}`;
  a.click();
  addPhotoLog('success', '⬇ Photo downloaded!');
}

function resetPhotoEditor() {
  photoImage = null;
  document.getElementById('photo-editor').style.display = 'none';
  document.getElementById('photo-upload-card').style.display = 'block';
  document.getElementById('photo-file-input').value = '';
  document.getElementById('photo-log').innerHTML = '<span class="log-line info">// Upload a photo to get started.</span>';
}

function addPhotoLog(type, msg) {
  const log = document.getElementById('photo-log');
  const line = document.createElement('span');
  line.className = `log-line ${type}`;
  line.textContent = msg;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

function makeAnother() {'''

content = content.replace(old_make_another, new_make_another, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Photo Editor tab added!")
