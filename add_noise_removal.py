with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add noise removal controls to enhancer
old_enhance_card = '''      <!-- ENHANCEMENTS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">✨</div>Enhancements</div>'''

new_enhance_card = '''      <!-- AUDIO ENHANCEMENT -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">🎙</div>Audio Enhancement</div>
        <div class="enhance-grid">
          <div class="form-group">
            <label class="form-label">Noise Reduction</label>
            <input type="range" class="filter-slider" id="noise-reduction" min="0" max="100" value="0" oninput="document.getElementById('noise-val').textContent=this.value+'%'">
            <span class="form-hint" id="noise-val">0%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Voice Boost</label>
            <input type="range" class="filter-slider" id="voice-boost" min="0" max="100" value="0" oninput="document.getElementById('voice-val').textContent=this.value+'%'">
            <span class="form-hint" id="voice-val">0%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Echo Removal</label>
            <input type="range" class="filter-slider" id="echo-removal" min="0" max="100" value="0" oninput="document.getElementById('echo-val').textContent=this.value+'%'">
            <span class="form-hint" id="echo-val">0%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Wind/Rumble Filter</label>
            <input type="range" class="filter-slider" id="wind-filter" min="0" max="100" value="0" oninput="document.getElementById('wind-val').textContent=this.value+'%'">
            <span class="form-hint" id="wind-val">0%</span>
          </div>
          <div class="form-group">
            <label class="form-label">Quick Preset</label>
            <select id="audio-preset" class="form-select" onchange="applyAudioPreset()">
              <option value="none">Custom</option>
              <option value="crowd">🎤 Crowd/Event Noise</option>
              <option value="outdoor">🌬 Outdoor/Wind</option>
              <option value="room">🏠 Room Echo</option>
              <option value="phone">📱 Phone Quality Fix</option>
              <option value="studio">🎙 Studio Clean</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Volume</label>
            <input type="range" class="filter-slider" id="audio-volume" min="0" max="300" value="100" oninput="document.getElementById('volume-val').textContent=this.value+'%'">
            <span class="form-hint" id="volume-val">100%</span>
          </div>
        </div>
      </div>

      <!-- ENHANCEMENTS -->
      <div class="card">
        <div class="card-title"><div class="card-title-icon">✨</div>Enhancements</div>'''

content = content.replace(old_enhance_card, new_enhance_card, 1)

# 2. Add audio processing JS
old_finish = 'function finishEnhancing() {'
new_finish = '''// ── AUDIO PROCESSING ──
function applyAudioPreset() {
  const preset = document.getElementById('audio-preset').value;
  const presets = {
    crowd:   { noise: 85, voice: 70, echo: 30, wind: 20, volume: 120 },
    outdoor: { noise: 60, voice: 50, echo: 10, wind: 90, volume: 110 },
    room:    { noise: 40, voice: 60, echo: 80, wind: 10, volume: 100 },
    phone:   { noise: 70, voice: 90, echo: 50, wind: 30, volume: 150 },
    studio:  { noise: 20, voice: 40, echo: 20, wind: 10, volume: 100 },
    none:    { noise: 0,  voice: 0,  echo: 0,  wind: 0,  volume: 100 }
  };
  const p = presets[preset] || presets.none;
  document.getElementById('noise-reduction').value = p.noise;
  document.getElementById('voice-boost').value = p.voice;
  document.getElementById('echo-removal').value = p.echo;
  document.getElementById('wind-filter').value = p.wind;
  document.getElementById('audio-volume').value = p.volume;
  document.getElementById('noise-val').textContent = p.noise + '%';
  document.getElementById('voice-val').textContent = p.voice + '%';
  document.getElementById('echo-val').textContent = p.echo + '%';
  document.getElementById('wind-val').textContent = p.wind + '%';
  document.getElementById('volume-val').textContent = p.volume + '%';
}

function buildAudioChain(audioCtx, source, dest) {
  const noiseLevel = parseInt(document.getElementById('noise-reduction').value) / 100;
  const voiceLevel = parseInt(document.getElementById('voice-boost').value) / 100;
  const echoLevel = parseInt(document.getElementById('echo-removal').value) / 100;
  const windLevel = parseInt(document.getElementById('wind-filter').value) / 100;
  const volume = parseInt(document.getElementById('audio-volume').value) / 100;

  let node = source;

  // Wind/Rumble filter - high pass filter removes low freq rumble
  if (windLevel > 0) {
    const highPass = audioCtx.createBiquadFilter();
    highPass.type = 'highpass';
    highPass.frequency.value = 80 + (windLevel * 120); // 80-200Hz cutoff
    highPass.Q.value = 0.7;
    node.connect(highPass);
    node = highPass;
  }

  // Noise reduction - combination of filters
  if (noiseLevel > 0) {
    // Low pass to cut high freq hiss
    const lowPass = audioCtx.createBiquadFilter();
    lowPass.type = 'lowpass';
    lowPass.frequency.value = 8000 - (noiseLevel * 4000); // 4000-8000Hz
    lowPass.Q.value = 0.5;
    node.connect(lowPass);
    node = lowPass;

    // Dynamics compressor to reduce noise floor
    const compressor = audioCtx.createDynamicsCompressor();
    compressor.threshold.value = -50 + (noiseLevel * 30); // -50 to -20dB
    compressor.knee.value = 10;
    compressor.ratio.value = 4 + (noiseLevel * 8); // 4:1 to 12:1
    compressor.attack.value = 0.003;
    compressor.release.value = 0.1 + (noiseLevel * 0.2);
    node.connect(compressor);
    node = compressor;
  }

  // Voice boost - peaking EQ around speech frequencies
  if (voiceLevel > 0) {
    // Boost 1-4kHz (speech clarity)
    const voiceEQ = audioCtx.createBiquadFilter();
    voiceEQ.type = 'peaking';
    voiceEQ.frequency.value = 2000;
    voiceEQ.Q.value = 1.5;
    voiceEQ.gain.value = voiceLevel * 12; // 0-12dB boost
    node.connect(voiceEQ);
    node = voiceEQ;

    // Boost presence 4-8kHz
    const presenceEQ = audioCtx.createBiquadFilter();
    presenceEQ.type = 'peaking';
    presenceEQ.frequency.value = 5000;
    presenceEQ.Q.value = 1;
    presenceEQ.gain.value = voiceLevel * 6;
    node.connect(presenceEQ);
    node = presenceEQ;
  }

  // Echo/reverb reduction - gate
  if (echoLevel > 0) {
    const echoComp = audioCtx.createDynamicsCompressor();
    echoComp.threshold.value = -30 - (echoLevel * 20);
    echoComp.ratio.value = 8 + (echoLevel * 12);
    echoComp.attack.value = 0.001;
    echoComp.release.value = 0.05 + (echoLevel * 0.1);
    node.connect(echoComp);
    node = echoComp;
  }

  // Volume
  const gainNode = audioCtx.createGain();
  gainNode.gain.value = volume;
  node.connect(gainNode);
  gainNode.connect(dest);

  return gainNode;
}

function finishEnhancing() {'''

content = content.replace(old_finish, new_finish, 1)

# 3. Update startEnhancing to use audio chain
old_video_source = '''  // Add original video audio
  const videoSource = audioCtx.createMediaElementSource(video);
  videoSource.connect(dest);
  videoSource.connect(audioCtx.destination);'''

new_video_source = '''  // Add original video audio with processing chain
  const videoSource = audioCtx.createMediaElementSource(video);
  buildAudioChain(audioCtx, videoSource, dest);
  // Also connect to speakers so user can hear during processing
  const monitorGain = audioCtx.createGain();
  monitorGain.gain.value = 0.5;
  videoSource.connect(monitorGain);
  monitorGain.connect(audioCtx.destination);'''

content = content.replace(old_video_source, new_video_source, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Audio noise removal added!")
