with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add MediaPipe script in head
old_head = '</style>\n</head>'
new_head = '''</style>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/selfie_segmentation.js" crossorigin="anonymous"></script>
</head>'''
content = content.replace(old_head, new_head, 1)

# 2. Add Remove Background button to photo editor export section
old_photo_download = '''        <div class="btn-row">
          <button onclick="downloadPhoto()" class="btn btn-green">⬇ Download Photo</button>
          <button onclick="resetPhotoEditor()" class="btn btn-outline">↺ Reset</button>
        </div>'''

new_photo_download = '''        <div class="btn-row">
          <button onclick="downloadPhoto()" class="btn btn-green">⬇ Download Photo</button>
          <button onclick="removeBackground()" class="btn btn-gold" id="bg-remove-btn">🗑 Remove Background</button>
          <button onclick="resetPhotoEditor()" class="btn btn-outline">↺ Reset</button>
        </div>
        <div id="bg-remove-status" style="display:none;margin-top:0.75rem;font-size:0.78rem;font-family:var(--font-mono);color:var(--gold);">
          ⏳ AI removing background...
        </div>'''

content = content.replace(old_photo_download, new_photo_download, 1)

# 3. Add background removal JS
old_add_photo_log = 'function addPhotoLog(type, msg) {'
new_add_photo_log = '''// ── AI BACKGROUND REMOVAL ──
let selfieSegmentation = null;

async function initSegmentation() {
  if (selfieSegmentation) return selfieSegmentation;
  selfieSegmentation = new SelfieSegmentation({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${file}`
  });
  selfieSegmentation.setOptions({ modelSelection: 1 });
  await selfieSegmentation.initialize();
  return selfieSegmentation;
}

async function removeBackground() {
  if (!photoImage) { alert('Upload a photo first'); return; }

  const btn = document.getElementById('bg-remove-btn');
  const status = document.getElementById('bg-remove-status');
  btn.disabled = true;
  btn.textContent = '⏳ Processing...';
  status.style.display = 'block';
  addPhotoLog('info', '🤖 AI detecting subject...');

  try {
    const segmentation = await initSegmentation();
    const canvas = document.getElementById('photo-canvas');
    const W = canvas.width;
    const H = canvas.height;

    // Create temp canvas with current edited photo
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = W;
    tempCanvas.height = H;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.filter = getPhotoFilter();
    tempCtx.drawImage(photoImage, 0, 0, W, H);
    tempCtx.filter = 'none';

    // Run segmentation
    let segmentationResult = null;
    segmentation.onResults((results) => {
      segmentationResult = results;
    });

    await segmentation.send({ image: tempCanvas });

    // Wait for result
    await new Promise(resolve => setTimeout(resolve, 500));

    if (!segmentationResult) {
      throw new Error('Segmentation failed');
    }

    // Apply mask - keep person, remove background
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, W, H);

    // Draw checkerboard for transparent bg preview
    const checkSize = 20;
    for (let x = 0; x < W; x += checkSize) {
      for (let y = 0; y < H; y += checkSize) {
        ctx.fillStyle = ((x/checkSize + y/checkSize) % 2 === 0) ? '#cccccc' : '#ffffff';
        ctx.fillRect(x, y, checkSize, checkSize);
      }
    }

    // Draw segmentation mask
    const maskCanvas = document.createElement('canvas');
    maskCanvas.width = W;
    maskCanvas.height = H;
    const maskCtx = maskCanvas.getContext('2d');
    maskCtx.drawImage(segmentationResult.segmentationMask, 0, 0, W, H);

    // Apply mask to photo
    ctx.save();
    ctx.globalCompositeOperation = 'source-over';

    // Draw the edited photo
    ctx.filter = getPhotoFilter();
    ctx.drawImage(photoImage, 0, 0, W, H);
    ctx.filter = 'none';

    // Use mask to cut out background
    ctx.globalCompositeOperation = 'destination-in';
    ctx.drawImage(maskCanvas, 0, 0, W, H);
    ctx.restore();

    // Change format to PNG for transparency
    document.getElementById('photo-format').value = 'png';

    addPhotoLog('success', '✓ Background removed! Download as PNG to keep transparency.');
    status.style.display = 'none';

  } catch(e) {
    addPhotoLog('error', '✗ Background removal failed: ' + e.message);
    status.style.display = 'none';
  }

  btn.disabled = false;
  btn.textContent = '🗑 Remove Background';
}

function addPhotoLog(type, msg) {'''

content = content.replace(old_add_photo_log, new_add_photo_log, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ AI Background Removal added!")
