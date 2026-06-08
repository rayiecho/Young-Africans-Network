with open('yan-studio.html', 'r') as f:
    content = f.read()

# Add quality presets card before audio enhancement
old_audio_card = '''      <!-- AUDIO ENHANCEMENT -->'''

new_audio_card = '''      <!-- QUALITY PRESETS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">✨</div>Quality Presets</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-bottom:1rem;">
          <button onclick="applyQualityPreset('iphone')" style="background:var(--navy3);border:1px solid var(--border);color:var(--white);padding:0.85rem;border-radius:10px;cursor:pointer;font-size:0.82rem;font-weight:600;transition:all 0.2s;" onmouseover="this.style.borderColor='var(--gold)'" onmouseout="this.style.borderColor='var(--border)'">📱 iPhone Look</button>
          <button onclick="applyQualityPreset('dslr')" style="background:var(--navy3);border:1px solid var(--border);color:var(--white);padding:0.85rem;border-radius:10px;cursor:pointer;font-size:0.82rem;font-weight:600;transition:all 0.2s;" onmouseover="this.style.borderColor='var(--gold)'" onmouseout="this.style.borderColor='var(--border)'">📷 DSLR Look</button>
          <button onclick="applyQualityPreset('cinema')" style="background:var(--navy3);border:1px solid var(--border);color:var(--white);padding:0.85rem;border-radius:10px;cursor:pointer;font-size:0.82rem;font-weight:600;transition:all 0.2s;" onmouseover="this.style.borderColor='var(--gold)'" onmouseout="this.style.borderColor='var(--border)'">🎬 Cinema</button>
          <button onclick="applyQualityPreset('broadcast')" style="background:var(--navy3);border:1px solid var(--border);color:var(--white);padding:0.85rem;border-radius:10px;cursor:pointer;font-size:0.82rem;font-weight:600;transition:all 0.2s;" onmouseover="this.style.borderColor='var(--gold)'" onmouseout="this.style.borderColor='var(--border)'">📺 Broadcast</button>
          <button onclick="applyQualityPreset('auto')" style="background:linear-gradient(135deg,rgba(245,166,35,0.2),rgba(45,138,94,0.2));border:1px solid var(--gold);color:var(--gold);padding:0.85rem;border-radius:10px;cursor:pointer;font-size:0.82rem;font-weight:700;">✨ Auto Enhance</button>
          <button onclick="applyQualityPreset('reset')" style="background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.85rem;border-radius:10px;cursor:pointer;font-size:0.82rem;">↺ Reset</button>
        </div>
        <div id="preset-applied" style="display:none;font-size:0.75rem;color:#74C69D;font-family:var(--font-mono);margin-top:0.5rem;"></div>
      </div>

      <!-- AUDIO ENHANCEMENT -->'''

content = content.replace(old_audio_card, new_audio_card, 1)

# Add quality preset JS function
old_audio_preset = 'function applyAudioPreset() {'
new_audio_preset = '''function applyQualityPreset(preset) {
  const presets = {
    iphone: {
      brightness: 108, contrast: 115, saturation: 125,
      sharpness: 2.5, filter: 'warm',
      label: '📱 iPhone Look applied'
    },
    dslr: {
      brightness: 102, contrast: 120, saturation: 110,
      sharpness: 3.5, filter: 'none',
      label: '📷 DSLR Look applied'
    },
    cinema: {
      brightness: 95, contrast: 130, saturation: 85,
      sharpness: 2, filter: 'cinematic',
      label: '🎬 Cinema Look applied'
    },
    broadcast: {
      brightness: 110, contrast: 112, saturation: 118,
      sharpness: 3, filter: 'none',
      label: '📺 Broadcast Look applied'
    },
    auto: {
      brightness: 105, contrast: 115, saturation: 115,
      sharpness: 2, filter: 'vivid',
      label: '✨ Auto Enhanced'
    },
    reset: {
      brightness: 100, contrast: 100, saturation: 100,
      sharpness: 0, filter: 'none',
      label: '↺ Reset to original'
    }
  };

  const p = presets[preset];
  if (!p) return;

  document.getElementById('adj-brightness').value = p.brightness;
  document.getElementById('adj-contrast').value = p.contrast;
  document.getElementById('adj-saturation').value = p.saturation;
  document.getElementById('adj-sharpness').value = p.sharpness;
  document.getElementById('enhance-filter').value = p.filter;

  document.getElementById('brightness-val').textContent = p.brightness + '%';
  document.getElementById('contrast-val').textContent = p.contrast + '%';
  document.getElementById('saturation-val').textContent = p.saturation + '%';
  document.getElementById('sharpness-val').textContent = p.sharpness;

  const label = document.getElementById('preset-applied');
  label.textContent = p.label;
  label.style.display = 'block';

  updatePreview();
  addEnhanceLog('success', '✓ ' + p.label);
}

function applyAudioPreset() {'''

content = content.replace(old_audio_preset, new_audio_preset, 1)

# Improve sharpness rendering in updatePreview
old_filter_css = '''function getFilterCSS() {
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
}'''

new_filter_css = '''function getFilterCSS() {
  const b = document.getElementById('adj-brightness').value;
  const c = document.getElementById('adj-contrast').value;
  const s = document.getElementById('adj-saturation').value;
  const sharp = parseFloat(document.getElementById('adj-sharpness').value);
  const filter = document.getElementById('enhance-filter').value;

  document.getElementById('brightness-val').textContent = b + '%';
  document.getElementById('contrast-val').textContent = c + '%';
  document.getElementById('saturation-val').textContent = s + '%';
  document.getElementById('sharpness-val').textContent = sharp;

  let filterStr = `brightness(${b}%) contrast(${c}%) saturate(${s}%)`;

  // Sharpness via contrast on edges
  if (sharp > 0) filterStr += ` contrast(${100 + sharp * 8}%)`;

  // Color filters
  if (filter === 'vivid') filterStr += ' saturate(150%) contrast(110%)';
  else if (filter === 'warm') filterStr += ' sepia(25%) saturate(120%) brightness(102%)';
  else if (filter === 'cool') filterStr += ' hue-rotate(15deg) saturate(85%) brightness(98%)';
  else if (filter === 'bw') filterStr += ' grayscale(100%) contrast(110%)';
  else if (filter === 'cinematic') filterStr += ' contrast(125%) saturate(75%) brightness(92%) sepia(10%)';

  return filterStr;
}'''

content = content.replace(old_filter_css, new_filter_css, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Quality presets added!")
