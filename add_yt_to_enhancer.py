with open('yan-studio.html', 'r') as f:
    content = f.read()

old = '''function finishEnhancing() {
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
}'''

new = '''let enhancedBlob = null;

function finishEnhancing() {
  enhancedBlob = new Blob(enhanceRecordedChunks, { type: 'video/webm' });
  const sizeMB = (enhancedBlob.size / 1024 / 1024).toFixed(1);
  addEnhanceLog('success', `✓ Enhanced video ready! Size: ${sizeMB}MB`);

  // Show download + YouTube buttons
  document.getElementById('enhance-export-btns').style.display = 'flex';
  
  document.getElementById('enhance-progress-label').textContent = 'Done!';
  document.getElementById('enhance-progress-pct').textContent = '100%';
  document.getElementById('enhance-progress-fill').style.width = '100%';
}

function downloadEnhanced() {
  if (!enhancedBlob) return;
  const url = URL.createObjectURL(enhancedBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `YAN-Enhanced-${Date.now()}.webm`;
  a.click();
  URL.revokeObjectURL(url);
  addEnhanceLog('success', '⬇ Downloaded!');
}

async function uploadEnhancedToYouTube() {
  if (!enhancedBlob) { alert('No enhanced video yet.'); return; }
  videoBlob = enhancedBlob;
  scriptData = { title: 'YAN Enhanced Video', hashtags: ['#YAN', '#YoungAfricansNetwork'] };
  await uploadToYouTube();
}'''

content = content.replace(old, new)

# Add export buttons to enhancer UI
old_enhance_actions = '''        <div class="btn-row">
          <button class="btn btn-gold" onclick="startEnhancing()">✨ Enhance & Export</button>
          <button class="btn btn-outline" onclick="resetEnhancer()">↺ Reset</button>
        </div>'''

new_enhance_actions = '''        <div class="btn-row">
          <button class="btn btn-gold" onclick="startEnhancing()">✨ Enhance & Export</button>
          <button class="btn btn-outline" onclick="resetEnhancer()">↺ Reset</button>
        </div>
        <div id="enhance-export-btns" style="display:none;" class="btn-row">
          <button class="btn btn-green" onclick="downloadEnhanced()">⬇ Download Enhanced</button>
          <button onclick="uploadEnhancedToYouTube()" style="background:#FF0000;border:none;color:#fff;padding:0.85rem 2rem;border-radius:10px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:0.5rem;">▶ Upload to YouTube</button>
          <button onclick="shareEnhancedWhatsApp()" style="background:#25D366;border:none;color:#fff;padding:0.85rem 2rem;border-radius:10px;font-weight:700;cursor:pointer;">💬 WhatsApp</button>
        </div>'''

content = content.replace(old_enhance_actions, new_enhance_actions, 1)

# Add WhatsApp share for enhanced
old_wa = 'function addEnhanceLog(type, msg) {'
new_wa = '''function shareEnhancedWhatsApp() {
  const text = `🎬 Check out this enhanced video!\\n\\nEnhanced with YAN Studio — AI Video Tool\\n\\n🌍 youngafricansnetwork.org/yan-studio.html\\n\\n#YAN #YoungAfricansNetwork`;
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
}

function addEnhanceLog(type, msg) {'''

content = content.replace(old_wa, new_wa, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ YouTube + WhatsApp added to enhancer!")
