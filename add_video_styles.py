with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add style selector to Step 1 form
old_style = '''              <option value="storytelling and narrative">Storytelling</option>
            </select>
          </div>'''

new_style = '''              <option value="storytelling and narrative">Storytelling</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Video Style</label>
            <select id="video-visual-style" class="form-select">
              <option value="slides">🖥 Slides (Default)</option>
              <option value="whiteboard">🖊 Whiteboard</option>
              <option value="cinematic">🎬 Cinematic</option>
            </select>
          </div>'''

content = content.replace(old_style, new_style, 1)

# 2. Add STYLES object and new drawScene after COLORS
old_colors = '''const COLORS = {
  navy: { bg: '#0A1628', text: '#F8F9FC', accent: '#F5A623' },
  green: { bg: '#0D2B1A', text: '#F8F9FC', accent: '#74C69D' },
  gold: { bg: '#2A1800', text: '#F8F9FC', accent: '#F5A623' },
  dark: { bg: '#050C14', text: '#F8F9FC', accent: '#F5A623' }
};'''

new_colors = '''const COLORS = {
  navy: { bg: '#0A1628', text: '#F8F9FC', accent: '#F5A623' },
  green: { bg: '#0D2B1A', text: '#F8F9FC', accent: '#74C69D' },
  gold: { bg: '#2A1800', text: '#F8F9FC', accent: '#F5A623' },
  dark: { bg: '#050C14', text: '#F8F9FC', accent: '#F5A623' }
};

// ── WHITEBOARD DRAW ──
function drawWhiteboardScene(canvas, scene, progress, currentWord = -1) {
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  // Blackboard background
  ctx.fillStyle = '#1a2e1a';
  ctx.fillRect(0, 0, W, H);

  // Chalk texture lines
  for (let i = 0; i < 8; i++) {
    ctx.strokeStyle = 'rgba(255,255,255,0.02)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, i * H/8);
    ctx.lineTo(W, i * H/8);
    ctx.stroke();
  }

  // Board border
  ctx.strokeStyle = '#8B6914';
  ctx.lineWidth = 12;
  ctx.strokeRect(6, 6, W-12, H-12);

  // YAN chalk logo top left
  ctx.fillStyle = 'rgba(255,255,255,0.7)';
  ctx.font = 'bold 13px Space Mono, monospace';
  ctx.textAlign = 'left';
  ctx.fillText('YAN STUDIO', 30, 36);

  // Draw title with chalk effect (appears progressively)
  const titleProgress = Math.min(progress * 3, 1);
  const title = scene.slideTitle || '';
  const titleChars = Math.floor(title.length * titleProgress);
  const titleText = title.substring(0, titleChars);

  ctx.font = `bold ${W > 800 ? 52 : 38}px 'Segoe UI', sans-serif`;
  ctx.fillStyle = 'rgba(255,255,250,0.92)';
  ctx.textAlign = 'center';
  ctx.shadowColor = 'rgba(255,255,255,0.3)';
  ctx.shadowBlur = 4;
  wrapText(ctx, titleText, W/2, H * 0.38, W*0.8, W > 800 ? 64 : 48);
  ctx.shadowBlur = 0;

  // Draw subtitle
  const subProgress = Math.min((progress - 0.3) * 3, 1);
  if (subProgress > 0) {
    const sub = scene.slideSubtitle || '';
    const subChars = Math.floor(sub.length * subProgress);
    ctx.font = `${W > 800 ? 26 : 20}px 'Segoe UI', sans-serif`;
    ctx.fillStyle = 'rgba(255,220,100,0.85)';
    ctx.textAlign = 'center';
    wrapText(ctx, sub.substring(0, subChars), W/2, H * 0.58, W*0.7, W > 800 ? 34 : 28);
  }

  // Chalk underline
  if (progress > 0.5) {
    const lineW = W * 0.4 * Math.min((progress - 0.5) * 4, 1);
    ctx.strokeStyle = 'rgba(255,220,100,0.6)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(W/2 - lineW/2, H * 0.68);
    ctx.lineTo(W/2 + lineW/2, H * 0.68);
    ctx.stroke();
  }

  // Progress bar
  ctx.fillStyle = 'rgba(255,255,255,0.1)';
  ctx.fillRect(0, H-6, W, 6);
  ctx.fillStyle = '#F5A623';
  ctx.fillRect(0, H-6, W * progress, 6);

  // Karaoke subtitles
  if (scene.voiceover && currentWord >= 0) {
    const words = scene.voiceover.split(' ');
    const subtitleY = H * 0.88;
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(0, subtitleY - 28, W, 48);
    const wordsPerLine = 7;
    const lineIndex = Math.floor(currentWord / wordsPerLine);
    const lineStart = lineIndex * wordsPerLine;
    const lineWords = words.slice(lineStart, lineStart + wordsPerLine);
    const currentWordInLine = currentWord - lineStart;
    ctx.font = 'bold 22px Syne, sans-serif';
    let totalWidth = 0;
    lineWords.forEach(w => { totalWidth += ctx.measureText(w + ' ').width; });
    let x = W/2 - totalWidth/2;
    lineWords.forEach((word, i) => {
      ctx.fillStyle = i === currentWordInLine ? '#F5A623' : i < currentWordInLine ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.85)';
      ctx.font = i === currentWordInLine ? 'bold 24px Syne, sans-serif' : 'bold 22px Syne, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(word, x, subtitleY + 8);
      x += ctx.measureText(word + ' ').width;
    });
  }
}

// ── CINEMATIC DRAW ──
function drawCinematicScene(canvas, scene, progress, currentWord = -1) {
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  // Deep cinematic background
  const bg = ctx.createLinearGradient(0, 0, W, H);
  const bgColors = {
    navy: ['#000814', '#001233'],
    green: ['#0a1f0a', '#0d3318'],
    gold: ['#1a0a00', '#2d1500'],
    dark: ['#000000', '#0a0a0a']
  };
  const bgc = bgColors[scene.background] || bgColors.navy;
  bg.addColorStop(0, bgc[0]);
  bg.addColorStop(1, bgc[1]);
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // Cinematic bars top and bottom
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, W, H * 0.1);
  ctx.fillRect(0, H * 0.9, W, H * 0.1);

  // Particle effect
  for (let i = 0; i < 30; i++) {
    const x = (W * ((i * 137.5) % 100)) / 100;
    const y = (H * ((i * 73.1 + progress * 20) % 100)) / 100;
    const size = (i % 3) + 1;
    ctx.fillStyle = `rgba(245,166,35,${0.1 + (i % 5) * 0.04})`;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fill();
  }

  // YAN branding
  ctx.fillStyle = 'rgba(245,166,35,0.6)';
  ctx.font = '11px Space Mono, monospace';
  ctx.textAlign = 'left';
  ctx.fillText('YOUNG AFRICANS NETWORK', 30, H * 0.15);

  // Scene number
  ctx.fillStyle = 'rgba(245,166,35,0.3)';
  ctx.font = 'bold 80px Syne, sans-serif';
  ctx.textAlign = 'right';
  ctx.fillText(`0${scene.sceneNumber}`, W - 40, H * 0.5 + 40);

  // Main title - dramatic entrance
  const titleOpacity = Math.min(progress * 4, 1);
  const titleX = W/2 + (1 - titleOpacity) * 60;
  ctx.globalAlpha = titleOpacity;
  ctx.fillStyle = '#F8F9FC';
  ctx.font = `bold ${W > 800 ? 56 : 40}px Syne, sans-serif`;
  ctx.textAlign = 'center';
  wrapText(ctx, scene.slideTitle, titleX, H * 0.42, W * 0.75, W > 800 ? 66 : 50);
  ctx.globalAlpha = 1;

  // Subtitle
  const subOpacity = Math.min(Math.max(progress * 3 - 0.5, 0), 1);
  ctx.globalAlpha = subOpacity;
  ctx.fillStyle = '#F5A623';
  ctx.font = `${W > 800 ? 24 : 18}px Syne, sans-serif`;
  ctx.textAlign = 'center';
  wrapText(ctx, scene.slideSubtitle, W/2, H * 0.6, W * 0.65, W > 800 ? 32 : 26);
  ctx.globalAlpha = 1;

  // Progress bar
  ctx.fillStyle = 'rgba(255,255,255,0.08)';
  ctx.fillRect(0, H * 0.9 - 3, W, 3);
  ctx.fillStyle = '#F5A623';
  ctx.fillRect(0, H * 0.9 - 3, W * progress, 3);

  // Karaoke subtitles
  if (scene.voiceover && currentWord >= 0) {
    const words = scene.voiceover.split(' ');
    const subtitleY = H * 0.82;
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.fillRect(0, subtitleY - 28, W, 48);
    const wordsPerLine = 7;
    const lineIndex = Math.floor(currentWord / wordsPerLine);
    const lineStart = lineIndex * wordsPerLine;
    const lineWords = words.slice(lineStart, lineStart + wordsPerLine);
    const currentWordInLine = currentWord - lineStart;
    ctx.font = 'bold 22px Syne, sans-serif';
    let totalWidth = 0;
    lineWords.forEach(w => { totalWidth += ctx.measureText(w + ' ').width; });
    let x = W/2 - totalWidth/2;
    lineWords.forEach((word, i) => {
      ctx.fillStyle = i === currentWordInLine ? '#F5A623' : i < currentWordInLine ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.85)';
      ctx.font = i === currentWordInLine ? 'bold 24px Syne, sans-serif' : 'bold 22px Syne, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(word, x, subtitleY + 8);
      x += ctx.measureText(word + ' ').width;
    });
  }
}'''

content = content.replace(old_colors, new_colors, 1)

# 3. Update drawScene call to route to correct style
old_draw = 'function drawScene(canvas, scene, progress, currentWord = -1) {'
new_draw = '''function drawScene(canvas, scene, progress, currentWord = -1) {
  const style = document.getElementById('video-visual-style') ? 
    document.getElementById('video-visual-style').value : 'slides';
  if (style === 'whiteboard') { drawWhiteboardScene(canvas, scene, progress, currentWord); return; }
  if (style === 'cinematic') { drawCinematicScene(canvas, scene, progress, currentWord); return; }
  // Default slides style below'''

content = content.replace(old_draw, new_draw, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Whiteboard + Cinematic styles added!")
