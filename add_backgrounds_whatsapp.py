with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add background image option to form
old_visual_style = '''          <div class="form-group">
            <label class="form-label">Video Style</label>
            <select id="video-visual-style" class="form-select">
              <option value="slides">🖥 Slides (Default)</option>
              <option value="whiteboard">🖊 Whiteboard</option>
              <option value="cinematic">🎬 Cinematic</option>
            </select>
          </div>'''

new_visual_style = '''          <div class="form-group">
            <label class="form-label">Video Style</label>
            <select id="video-visual-style" class="form-select">
              <option value="slides">🖥 Slides (Default)</option>
              <option value="whiteboard">🖊 Whiteboard</option>
              <option value="cinematic">🎬 Cinematic</option>
              <option value="photobg">🌍 Photo Background</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Background Theme</label>
            <select id="bg-theme" class="form-select">
              <option value="africa">🌍 Africa</option>
              <option value="education">📚 Education</option>
              <option value="technology">💻 Technology</option>
              <option value="nature">🌿 Nature</option>
              <option value="youth">👥 Youth</option>
              <option value="city">🏙 City</option>
              <option value="abstract">✨ Abstract</option>
            </select>
          </div>'''

content = content.replace(old_visual_style, new_visual_style, 1)

# 2. Add WhatsApp share button on download page
old_download_btns = '''          <button class="btn btn-green" id="btn-download" onclick="downloadVideo()">⬇ Download WebM</button>
          <button class="btn btn-gold" onclick="downloadMP4()">🎬 Download MP4</button>
          <button class="btn btn-outline" onclick="makeAnother()">+ Make Another Video</button>'''

new_download_btns = '''          <button class="btn btn-green" id="btn-download" onclick="downloadVideo()">⬇ Download WebM</button>
          <button class="btn btn-gold" onclick="downloadMP4()">🎬 Download MP4</button>
          <button class="btn btn-outline" onclick="shareWhatsApp()" style="background:#25D366;border-color:#25D366;color:#fff;">💬 Share on WhatsApp</button>
          <button class="btn btn-outline" onclick="makeAnother()">+ Make Another Video</button>'''

content = content.replace(old_download_btns, new_download_btns, 1)

# 3. Add photo background draw function + WhatsApp share
old_wrap_func = 'function applyTransition(canvas) {'
new_wrap_func = '''// ── BACKGROUND IMAGES ──
const bgImageCache = {};

async function loadBgImage(theme) {
  if (bgImageCache[theme]) return bgImageCache[theme];
  const queries = {
    africa: 'africa landscape savanna',
    education: 'students learning africa classroom',
    technology: 'technology computer africa',
    nature: 'africa nature green',
    youth: 'african youth community',
    city: 'africa city skyline',
    abstract: 'abstract colorful geometric'
  };
  const query = queries[theme] || 'africa';
  const url = `https://source.unsplash.com/1280x720/?${encodeURIComponent(query)}`;
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => { bgImageCache[theme] = img; resolve(img); };
    img.onerror = () => resolve(null);
    img.src = url;
  });
}

function drawPhotoBgScene(canvas, scene, progress, currentWord = -1, bgImg = null) {
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const colors = { accent: '#F5A623', text: '#F8F9FC' };

  // Background image or fallback
  if (bgImg) {
    ctx.drawImage(bgImg, 0, 0, W, H);
  } else {
    ctx.fillStyle = '#0A1628';
    ctx.fillRect(0, 0, W, H);
  }

  // Dark overlay for readability
  const overlay = ctx.createLinearGradient(0, 0, 0, H);
  overlay.addColorStop(0, 'rgba(0,0,0,0.5)');
  overlay.addColorStop(0.5, 'rgba(0,0,0,0.65)');
  overlay.addColorStop(1, 'rgba(0,0,0,0.8)');
  ctx.fillStyle = overlay;
  ctx.fillRect(0, 0, W, H);

  // YAN branding
  ctx.fillStyle = 'rgba(245,166,35,0.9)';
  ctx.font = 'bold 13px Space Mono, monospace';
  ctx.textAlign = 'left';
  ctx.fillText('YOUNG AFRICANS NETWORK', 24, 36);
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.font = '11px Space Mono, monospace';
  ctx.fillText('youngafricansnetwork.org', 24, 54);

  // Scene number badge
  ctx.fillStyle = 'rgba(245,166,35,0.2)';
  roundRect(ctx, W-90, 10, 80, 30, 8);
  ctx.fill();
  ctx.fillStyle = '#F5A623';
  ctx.font = '10px Space Mono, monospace';
  ctx.textAlign = 'center';
  ctx.fillText(`SCENE ${scene.sceneNumber}`, W-50, 30);

  // Main title with shadow
  ctx.shadowColor = 'rgba(0,0,0,0.8)';
  ctx.shadowBlur = 20;
  ctx.fillStyle = '#FFFFFF';
  ctx.font = `bold ${W > 800 ? 52 : 38}px Syne, sans-serif`;
  ctx.textAlign = 'center';
  wrapText(ctx, scene.slideTitle, W/2, H * 0.4, W * 0.8, W > 800 ? 62 : 48);

  // Subtitle
  ctx.fillStyle = '#F5A623';
  ctx.font = `${W > 800 ? 24 : 18}px Syne, sans-serif`;
  ctx.shadowBlur = 10;
  wrapText(ctx, scene.slideSubtitle, W/2, H * 0.58, W * 0.7, W > 800 ? 32 : 26);
  ctx.shadowBlur = 0;

  // Progress bar
  ctx.fillStyle = 'rgba(255,255,255,0.15)';
  ctx.fillRect(0, H-5, W, 5);
  ctx.fillStyle = '#F5A623';
  ctx.fillRect(0, H-5, W * progress, 5);

  // Word reveal
  if (scene.voiceover && currentWord >= 0) {
    const words = scene.voiceover.split(' ');
    const wordsPerLine = 6;
    const lineHeight = 34;
    const startY = H * 0.15;
    const maxLines = Math.floor((H * 0.75) / lineHeight);
    const lines = [];
    for (let i = 0; i < words.length; i += wordsPerLine) lines.push(words.slice(i, i + wordsPerLine));
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(W * 0.05, startY - 10, W * 0.9, Math.min(lines.length, maxLines) * lineHeight + 20);
    lines.forEach((lineWords, lineIdx) => {
      if (lineIdx >= maxLines) return;
      const y = startY + lineIdx * lineHeight;
      const lineStartWord = lineIdx * wordsPerLine;
      let x = W * 0.08;
      lineWords.forEach((word, wordIdx) => {
        const globalIdx = lineStartWord + wordIdx;
        if (globalIdx > currentWord) return;
        ctx.shadowColor = globalIdx === currentWord ? '#F5A623' : 'transparent';
        ctx.shadowBlur = globalIdx === currentWord ? 12 : 0;
        ctx.fillStyle = globalIdx === currentWord ? '#F5A623' : 'rgba(255,255,255,0.9)';
        ctx.font = `bold ${globalIdx === currentWord ? 26 : 24}px Syne, sans-serif`;
        ctx.textAlign = 'left';
        ctx.fillText(word, x, y + 24);
        ctx.shadowBlur = 0;
        x += ctx.measureText(word + ' ').width + 4;
      });
    });
  }
}

// ── WHATSAPP SHARE ──
function shareWhatsApp() {
  if (!scriptData) return;
  const text = `🎬 *${scriptData.title}*\\n\\nGenerated with YAN Studio — AI Video Generator\\n\\n🌍 youngafricansnetwork.org/yan-studio.html\\n\\n#YAN #YoungAfricansNetwork #AIVideo`;
  const url = `https://wa.me/?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
}

function applyTransition(canvas) {'''

content = content.replace(old_wrap_func, new_wrap_func, 1)

# 4. Wire photo background into drawScene routing
old_routing = "  if (style === 'whiteboard') { drawWhiteboardScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }\n  if (style === 'cinematic') { drawCinematicScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }"

new_routing = """  if (style === 'whiteboard') { drawWhiteboardScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }
  if (style === 'cinematic') { drawCinematicScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }
  if (style === 'photobg') {
    const theme = document.getElementById('bg-theme') ? document.getElementById('bg-theme').value : 'africa';
    const cachedImg = bgImageCache[theme] || null;
    drawPhotoBgScene(canvas, scene, progress, currentWord, cachedImg);
    applyTransition(canvas);
    return;
  }"""

content = content.replace(old_routing, new_routing, 1)

# 5. Preload background image when recording starts
old_preload = "  addLog('info', '🎤 Generating voiceover audio...');\n  // Music will start after AudioContext is set up"
new_preload = """  // Preload background image if needed
  const visualStyle = document.getElementById('video-visual-style') ? document.getElementById('video-visual-style').value : 'slides';
  if (visualStyle === 'photobg') {
    const theme = document.getElementById('bg-theme').value;
    addLog('info', '🖼 Loading background image...');
    await loadBgImage(theme);
    addLog('success', '✓ Background image loaded');
  }
  addLog('info', '🎤 Generating voiceover audio...');
  // Music will start after AudioContext is set up"""

content = content.replace(old_preload, new_preload, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Photo backgrounds + WhatsApp share added!")
