with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add presenter photo UI to form
old_bg = '            <label class="form-label">Background Theme</label>'
new_bg = '''            <label class="form-label">Presenter Photo</label>
            <div style="display:flex;gap:0.75rem;align-items:center;flex-wrap:wrap;">
              <input type="file" id="presenter-photo" accept="image/*" style="display:none" onchange="loadPresenterPhoto(event)">
              <button onclick="document.getElementById('presenter-photo').click()" style="background:var(--navy3);border:1px solid var(--border);color:var(--white);padding:0.65rem 1rem;border-radius:8px;font-size:0.82rem;cursor:pointer;">📷 Upload Photo</button>
              <span id="presenter-photo-name" style="font-size:0.75rem;color:var(--muted);font-family:var(--font-mono);">No photo</span>
              <button id="presenter-clear-btn" onclick="clearPresenterPhoto()" style="display:none;background:none;border:none;color:var(--red);cursor:pointer;">✕</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Photo Position</label>
            <select id="presenter-position" class="form-select">
              <option value="br">Bottom Right</option>
              <option value="bl">Bottom Left</option>
              <option value="tr">Top Right</option>
              <option value="tl">Top Left</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Photo Shape</label>
            <select id="presenter-shape" class="form-select">
              <option value="circle">Circle</option>
              <option value="square">Rounded Square</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Background Theme</label>'''

content = content.replace(old_bg, new_bg, 1)

# 2. Add JS functions before VIDEO GENERATION comment
old_js = '// ── VIDEO GENERATION ──'
new_js = '''// ── PRESENTER PHOTO ──
let presenterImage = null;

function loadPresenterPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const img = new Image();
    img.onload = () => {
      presenterImage = img;
      document.getElementById('presenter-photo-name').textContent = file.name;
      document.getElementById('presenter-clear-btn').style.display = 'inline';
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function clearPresenterPhoto() {
  presenterImage = null;
  document.getElementById('presenter-photo').value = '';
  document.getElementById('presenter-photo-name').textContent = 'No photo';
  document.getElementById('presenter-clear-btn').style.display = 'none';
}

function drawPresenterPhoto(ctx, W, H) {
  if (!presenterImage) return;
  const position = document.getElementById('presenter-position') ? document.getElementById('presenter-position').value : 'br';
  const shape = document.getElementById('presenter-shape') ? document.getElementById('presenter-shape').value : 'circle';
  const size = Math.round(W * 0.15);
  const margin = 20;
  let x, y;
  if (position === 'br') { x = W - size - margin; y = H - size - margin - 20; }
  else if (position === 'bl') { x = margin; y = H - size - margin - 20; }
  else if (position === 'tr') { x = W - size - margin; y = margin + 70; }
  else { x = margin; y = margin + 70; }
  ctx.save();
  ctx.shadowColor = '#F5A623';
  ctx.shadowBlur = 12;
  ctx.strokeStyle = '#F5A623';
  ctx.lineWidth = 3;
  ctx.beginPath();
  if (shape === 'circle') {
    ctx.arc(x + size/2, y + size/2, size/2, 0, Math.PI * 2);
  } else {
    const r = 12;
    ctx.moveTo(x + r, y); ctx.lineTo(x + size - r, y);
    ctx.quadraticCurveTo(x + size, y, x + size, y + r);
    ctx.lineTo(x + size, y + size - r);
    ctx.quadraticCurveTo(x + size, y + size, x + size - r, y + size);
    ctx.lineTo(x + r, y + size);
    ctx.quadraticCurveTo(x, y + size, x, y + size - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }
  ctx.stroke();
  ctx.clip();
  ctx.drawImage(presenterImage, x, y, size, size);
  ctx.restore();
  ctx.shadowBlur = 0;
}

// ── VIDEO GENERATION ──'''

content = content.replace(old_js, new_js, 1)

# 3. Call drawPresenterPhoto in slides drawScene
old_bottom = "  ctx.fillText('BUILDING THE FUTURE, TOGETHER', W/2, H*0.91 + 18);"
new_bottom = "  ctx.fillText('BUILDING THE FUTURE, TOGETHER', W/2, H*0.91 + 18);\n  drawPresenterPhoto(ctx, W, H);"
content = content.replace(old_bottom, new_bottom, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("Done")
