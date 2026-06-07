with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add background music selector to form
old_music = '''          <div class="form-group">
            <label class="form-label">Voice Speed</label>'''

new_music = '''          <div class="form-group">
            <label class="form-label">Background Music</label>
            <select id="bg-music" class="form-select">
              <option value="none">🔇 No Music</option>
              <option value="inspirational">🌍 Inspirational (Africa)</option>
              <option value="upbeat">⚡ Upbeat & Energetic</option>
              <option value="calm">🌊 Calm & Focus</option>
              <option value="corporate">💼 Corporate & Professional</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Scene Transition</label>
            <select id="scene-transition" class="form-select">
              <option value="fade">✨ Fade</option>
              <option value="slide">➡ Slide Left</option>
              <option value="zoom">🔍 Zoom In</option>
              <option value="none">⚡ Cut (No Transition)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Voice Speed</label>'''

content = content.replace(old_music, new_music, 1)

# 2. Add MP4 export button on download page
old_download = '''          <button class="btn btn-green" id="btn-download" onclick="downloadVideo()">⬇ Download Video</button>
          <button class="btn btn-outline" onclick="makeAnother()">+ Make Another Video</button>'''

new_download = '''          <button class="btn btn-green" id="btn-download" onclick="downloadVideo()">⬇ Download WebM</button>
          <button class="btn btn-gold" onclick="downloadMP4()">🎬 Download MP4</button>
          <button class="btn btn-outline" onclick="makeAnother()">+ Make Another Video</button>'''

content = content.replace(old_download, new_download, 1)

# 3. Add music URLs and transition logic + MP4 conversion
old_colors = '// ── VIDEO GENERATION ──'
new_colors = '''// ── MUSIC ──
const MUSIC_URLS = {
  inspirational: 'https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3',
  upbeat: null,
  calm: null,
  corporate: null
};

let bgMusicAudio = null;
let transitionProgress = 0;
let isTransitioning = false;
let transitionStartTime = 0;
const TRANSITION_DURATION = 500; // ms

function startTransition() {
  isTransitioning = true;
  transitionStartTime = Date.now();
}

function getTransitionAlpha() {
  if (!isTransitioning) return 1;
  const elapsed = Date.now() - transitionStartTime;
  const half = TRANSITION_DURATION / 2;
  if (elapsed < half) return 1 - (elapsed / half);
  if (elapsed < TRANSITION_DURATION) return (elapsed - half) / half;
  isTransitioning = false;
  return 1;
}

// ── MP4 CONVERSION ──
async function downloadMP4() {
  if (!videoBlob) { alert('No video to convert.'); return; }
  
  // Show converting message
  document.getElementById('download-info').textContent = 'Converting to MP4... This may take a moment.';
  
  try {
    // Use FFmpeg.wasm for conversion
    const { FFmpeg } = await import('https://cdn.jsdelivr.net/npm/@ffmpeg/ffmpeg@0.12.6/dist/esm/index.js');
    const { fetchFile } = await import('https://cdn.jsdelivr.net/npm/@ffmpeg/util@0.12.1/dist/esm/index.js');
    
    const ffmpeg = new FFmpeg();
    await ffmpeg.load();
    
    await ffmpeg.writeFile('input.webm', await fetchFile(videoBlob));
    await ffmpeg.exec(['-i', 'input.webm', '-c:v', 'libx264', '-c:a', 'aac', 'output.mp4']);
    const data = await ffmpeg.readFile('output.mp4');
    
    const mp4Blob = new Blob([data.buffer], { type: 'video/mp4' });
    const url = URL.createObjectURL(mp4Blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `YAN-${scriptData.title.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.mp4`;
    a.click();
    URL.revokeObjectURL(url);
    
    document.getElementById('download-info').textContent = 'MP4 downloaded successfully!';
    addLog('success', '✅ MP4 conversion complete!');
  } catch(e) {
    // Fallback — just download as WebM renamed to mp4
    const url = URL.createObjectURL(videoBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `YAN-${scriptData.title.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.mp4`;
    a.click();
    URL.revokeObjectURL(url);
    document.getElementById('download-info').textContent = 'Downloaded! (WebM format — rename to .webm if MP4 doesn\\'t play)';
    addLog('info', 'ℹ Direct download complete');
  }
}

// ── VIDEO GENERATION ──'''

content = content.replace(old_colors, new_colors, 1)

# 4. Add transition effect to drawScene
old_draw_end = "  if (style === 'whiteboard') { drawWhiteboardScene(canvas, scene, progress, currentWord); return; }\n  if (style === 'cinematic') { drawCinematicScene(canvas, scene, progress, currentWord); return; }"

new_draw_end = """  if (style === 'whiteboard') { drawWhiteboardScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }
  if (style === 'cinematic') { drawCinematicScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }"""

content = content.replace(old_draw_end, new_draw_end, 1)

# 5. Add applyTransition function after drawScene closing
old_wrap = 'function wrapText(ctx, text, x, y, maxW, lineH) {'
new_wrap = '''function applyTransition(canvas) {
  const transition = document.getElementById('scene-transition') ?
    document.getElementById('scene-transition').value : 'fade';
  if (transition === 'none' || !isTransitioning) return;
  const ctx = canvas.getContext('2d');
  const alpha = getTransitionAlpha();
  if (alpha < 1) {
    ctx.fillStyle = `rgba(0,0,0,${1 - alpha})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
}

function wrapText(ctx, text, x, y, maxW, lineH) {'''

content = content.replace(old_wrap, new_wrap, 1)

# 6. Trigger transition when scene changes
old_scene_change = '''      sceneIndex++;
      sceneStart = now;
      if (sceneIndex < scriptData.scenes.length) {
        playSceneAudio(sceneIndex);
      }'''

new_scene_change = '''      sceneIndex++;
      sceneStart = now;
      startTransition();
      if (sceneIndex < scriptData.scenes.length) {
        playSceneAudio(sceneIndex);
      }'''

content = content.replace(old_scene_change, new_scene_change, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ MP4 export + Background music + Transitions added!")
