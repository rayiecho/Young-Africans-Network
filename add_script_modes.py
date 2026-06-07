with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add mode toggle CSS
old_css = '  /* RESPONSIVE */'
new_css = '''  /* MODE TOGGLE */
  .mode-toggle { display: flex; gap: 0; margin-bottom: 1.5rem; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
  .mode-btn { flex: 1; padding: 0.85rem; background: transparent; border: none; color: var(--muted); font-family: var(--font-display); font-size: 0.88rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
  .mode-btn.active { background: var(--gold); color: var(--navy); }
  .mode-btn:hover:not(.active) { background: rgba(245,166,35,0.08); color: var(--white); }

  /* RESPONSIVE */'''

content = content.replace(old_css, new_css, 1)

# 2. Add mode toggle HTML before form-grid
old_form = '        <div class="form-grid">'
new_form = '''        <!-- MODE TOGGLE -->
        <div class="mode-toggle" style="margin-bottom:1.5rem;">
          <button class="mode-btn active" id="mode-ai" onclick="setMode(\'ai\')">🤖 AI Generate Script</button>
          <button class="mode-btn" id="mode-own" onclick="setMode(\'own\')">✍️ Use My Own Script</button>
        </div>

        <!-- AI MODE FIELDS -->
        <div id="ai-fields">
        <div class="form-grid">'''

content = content.replace(old_form, new_form, 1)

# 3. Close ai-fields div and add own-script fields after the form-grid
old_end = '''        <div class="btn-row">
          <button class="btn btn-gold" onclick="generateScript()">
            ✨ Generate Script
          </button>
        </div>'''

new_end = '''        </div><!-- end form-grid -->
        </div><!-- end ai-fields -->

        <!-- OWN SCRIPT MODE -->
        <div id="own-fields" style="display:none;">
          <div class="form-group full" style="margin-bottom:1.25rem;">
            <label class="form-label">Your Script / Content</label>
            <textarea id="own-script" class="form-textarea" style="min-height:250px;" placeholder="Paste your full script here...

Example:
Scene 1: Introduction
Welcome to Young Africans Network. We are a pan-African organization...

Scene 2: Our Programs
We offer 6 programs including IT Training, Scholarships...

Or just paste your raw content and we will structure it into scenes automatically."></textarea>
            <span class="form-hint">Paste your script, article, notes or any content. AI will structure it into video scenes.</span>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Video Duration</label>
              <select id="own-duration" class="form-select">
                <option value="30">30 seconds</option>
                <option value="60" selected>1 minute</option>
                <option value="90">90 seconds</option>
                <option value="120">2 minutes</option>
                <option value="180">3 minutes</option>
                <option value="300">5 minutes</option>
                <option value="600">10 minutes</option>
                <option value="900">15 minutes</option>
                <option value="1200">20 minutes</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Voice Speed</label>
              <select id="own-voice-speed" class="form-select">
                <option value="0.85">Slow & Clear</option>
                <option value="0.95" selected>Normal</option>
                <option value="1.05">Slightly Fast</option>
              </select>
            </div>
          </div>
        </div>

        <div class="btn-row">
          <button class="btn btn-gold" id="btn-generate" onclick="generateScript()">
            ✨ Generate Script
          </button>
        </div>'''

content = content.replace(old_end, new_end, 1)

# 4. Add setMode function and update generateScript
old_script = '// ── STEPS ──'
new_script = '''// ── MODE ──
let currentMode = 'ai';

function setMode(mode) {
  currentMode = mode;
  document.getElementById('ai-fields').style.display = mode === 'ai' ? 'block' : 'none';
  document.getElementById('own-fields').style.display = mode === 'own' ? 'block' : 'none';
  document.getElementById('mode-ai').classList.toggle('active', mode === 'ai');
  document.getElementById('mode-own').classList.toggle('active', mode === 'own');
  document.getElementById('btn-generate').textContent = mode === 'ai' ? '✨ Generate Script' : '🎬 Structure My Script';
}

// ── STEPS ──'''

content = content.replace(old_script, new_script, 1)

# 5. Update generateScript to handle own mode
old_gen = "async function generateScript() {\n  const topic = document.getElementById('video-topic').value.trim();\n  if (!topic) { alert('Please enter a video topic first.'); return; }"

new_gen = """async function generateScript() {
  if (currentMode === 'own') {
    await structureOwnScript();
    return;
  }
  const topic = document.getElementById('video-topic').value.trim();
  if (!topic) { alert('Please enter a video topic first.'); return; }"""

content = content.replace(old_gen, new_gen, 1)

# 6. Add structureOwnScript function before generateScript
old_func = 'async function generateScript() {'
new_func = '''async function structureOwnScript() {
  const ownScript = document.getElementById('own-script').value.trim();
  if (!ownScript) { alert('Please paste your script first.'); return; }

  const duration = document.getElementById('own-duration').value;
  const speed = document.getElementById('own-voice-speed').value;

  // Sync speed to main voice speed
  document.getElementById('voice-speed').value = speed;

  document.getElementById('loading-script').style.display = 'block';
  document.querySelector('#panel-1 .card').style.display = 'none';

  const scenes = parseInt(duration) <= 30 ? 3 : parseInt(duration) <= 60 ? 4 : parseInt(duration) <= 90 ? 5 : parseInt(duration) <= 120 ? 6 : parseInt(duration) <= 180 ? 8 : parseInt(duration) <= 300 ? 12 : parseInt(duration) <= 600 ? 20 : parseInt(duration) <= 900 ? 28 : 35;
  const words = Math.round((parseInt(duration) / 60) * 130);

  const prompt = `You are YAN Studio. Structure the following content into a ${duration}-second video script for Young Africans Network.

Content to structure:
${ownScript}

Return ONLY a JSON object:
{
  "title": "Video title",
  "duration": ${duration},
  "totalWords": ${words},
  "scenes": [
    {
      "sceneNumber": 1,
      "slideTitle": "Short headline (max 6 words)",
      "slideSubtitle": "Short subtitle (max 10 words)",
      "voiceover": "Exact words for this scene taken from the provided content",
      "duration": ${Math.round(parseInt(duration)/scenes)},
      "background": "navy"
    }
  ],
  "callToAction": "CTA text",
  "hashtags": ["#YAN"]
}

Make exactly ${scenes} scenes. Use the provided content for voiceover text — do not invent new content.`;

  try {
    const response = await fetch('https://yan-ai-worker.youngafricansn.workers.dev', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 2000,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    const data = await response.json();
    let text = '';
    if (data.content && data.content[0]) text = data.content[0].text.trim();
    const clean = text.replace(/```json|```/g, '').trim();
    scriptData = JSON.parse(clean);
    renderScript();
    document.getElementById('loading-script').style.display = 'none';
    document.querySelector('#panel-1 .card').style.display = 'block';
    goToStep(2);
  } catch(err) {
    document.getElementById('loading-script').style.display = 'none';
    document.querySelector('#panel-1 .card').style.display = 'block';
    alert('Failed to structure script. Please try again.');
  }
}

async function generateScript() {'''

content = content.replace(old_func, new_func, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Two-mode script system added!")
