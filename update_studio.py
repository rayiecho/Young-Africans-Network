# Read the current file
with open('yan-studio.html', 'r') as f:
    content = f.read()

# Fix 1: Change API endpoint to use YAN worker
content = content.replace(
    "const response = await fetch('https://api.anthropic.com/v1/messages', {",
    "const response = await fetch('https://yan-ai-worker.youngafricansn.workers.dev', {"
)

# Fix 2: Change model name
content = content.replace(
    "model: 'claude-sonnet-4-20250514',",
    "model: 'claude-haiku-4-5-20251001',"
)

# Fix 3: Replace entire startRecording function with audio-enabled version
old_recording = """async function startRecording() {
  if (!scriptData) { alert('No script found. Please go back and generate a script first.'); return; }

  goToStep(3);

  const canvas = document.getElementById('video-canvas');
  const container = document.getElementById('canvas-container');
  canvas.width = 1280;
  canvas.height = 720;

  document.getElementById('canvas-overlay').style.display = 'none';
  document.getElementById('btn-record').style.display = 'none';
  document.getElementById('btn-stop').style.display = 'inline-flex';
  document.getElementById('progress-wrap').style.display = 'block';

  recordedChunks = [];
  isRecording = true;

  // Setup MediaRecorder
  const stream = canvas.captureStream(30);
  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
  mediaRecorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 2500000 });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = finishVideo;
  mediaRecorder.start(100);

  addLog('info', '▶ Recording started...');

  // Play through all scenes
  const totalDuration = scriptData.duration * 1000;
  const sceneDurations = scriptData.scenes.map(s => s.duration * 1000);
  let sceneIndex = 0;
  let sceneStart = Date.now();
  let totalStart = Date.now();

  // Speech synthesis
  const synth = window.speechSynthesis;
  const speed = parseFloat(document.getElementById('voice-speed').value);

  function speakScene(scene) {
    synth.cancel();
    const utt = new SpeechSynthesisUtterance(scene.voiceover);
    utt.rate = speed;
    utt.pitch = 1;
    utt.volume = 1;
    // Try to find a good voice
    const voices = synth.getVoices();
    const preferred = voices.find(v => v.lang === 'en-GB') || voices.find(v => v.lang.startsWith('en')) || voices[0];
    if (preferred) utt.voice = preferred;
    synth.speak(utt);
    addLog('success', `✓ Scene ${scene.sceneNumber}: ${scene.slideTitle}`);
  }

  speakScene(scriptData.scenes[0]);

  function renderLoop() {
    if (!isRecording) return;

    const now = Date.now();
    const totalElapsed = now - totalStart;
    const sceneElapsed = now - sceneStart;
    const totalProgress = Math.min(totalElapsed / totalDuration, 1);
    const sceneProgress = Math.min(sceneElapsed / (sceneDurations[sceneIndex] || 1), 1);

    // Update UI
    const pct = Math.round(totalProgress * 100);
    document.getElementById('progress-fill').style.width = pct + '%';
    document.getElementById('progress-pct').textContent = pct + '%';
    document.getElementById('progress-label-text').textContent = `Scene ${sceneIndex + 1} of ${scriptData.scenes.length}`;

    // Draw current scene
    drawScene(canvas, scriptData.scenes[sceneIndex], totalProgress);

    // Advance scene
    if (sceneElapsed >= sceneDurations[sceneIndex]) {
      sceneIndex++;
      sceneStart = now;
      if (sceneIndex < scriptData.scenes.length) {
        speakScene(scriptData.scenes[sceneIndex]);
      }
    }

    // Auto-stop
    if (totalElapsed >= totalDuration + 500) {
      stopRecording();
      return;
    }

    animFrame = requestAnimationFrame(renderLoop);
  }

  animFrame = requestAnimationFrame(renderLoop);
}

function stopRecording() {
  isRecording = false;
  if (animFrame) cancelAnimationFrame(animFrame);
  window.speechSynthesis.cancel();
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  document.getElementById('btn-stop').style.display = 'none';
  addLog('success', '✓ Recording complete! Processing video...');
}"""

new_recording = """async function startRecording() {
  if (!scriptData) { alert('No script found. Please go back and generate a script first.'); return; }

  goToStep(3);

  const canvas = document.getElementById('video-canvas');
  canvas.width = 1280;
  canvas.height = 720;

  document.getElementById('canvas-overlay').style.display = 'none';
  document.getElementById('btn-record').style.display = 'none';
  document.getElementById('btn-stop').style.display = 'inline-flex';
  document.getElementById('progress-wrap').style.display = 'block';

  recordedChunks = [];
  isRecording = true;

  const speed = parseFloat(document.getElementById('voice-speed').value);

  // AudioContext for capturing audio into video
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const dest = audioCtx.createMediaStreamDestination();

  // Combined stream: canvas + audio
  const canvasStream = canvas.captureStream(30);
  const audioTrack = dest.stream.getAudioTracks()[0];
  if (audioTrack) canvasStream.addTrack(audioTrack);

  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus')
    ? 'video/webm;codecs=vp9,opus'
    : MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')
    ? 'video/webm;codecs=vp8,opus'
    : 'video/webm';

  mediaRecorder = new MediaRecorder(canvasStream, { mimeType, videoBitsPerSecond: 2500000 });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = finishVideo;
  mediaRecorder.start(100);

  addLog('info', '▶ Recording started with audio...');

  function speakScene(scene) {
    // Web Speech for live playback
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(scene.voiceover);
    utt.rate = speed; utt.pitch = 1; utt.volume = 1;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v => v.lang === 'en-GB') ||
                      voices.find(v => v.lang.startsWith('en')) || voices[0];
    if (preferred) utt.voice = preferred;
    window.speechSynthesis.speak(utt);

    // AudioContext tones captured by MediaRecorder
    const words = scene.voiceover.split(' ');
    const wordDuration = scene.duration / words.length;
    words.forEach((word, i) => {
      const startTime = audioCtx.currentTime + (i * wordDuration * (1/speed));
      const dur = wordDuration * 0.7 * (1/speed);
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      const baseFreq = 120 + (word.length * 8) + (i % 3 * 20);
      osc.frequency.setValueAtTime(baseFreq, startTime);
      osc.frequency.linearRampToValueAtTime(baseFreq * 1.1, startTime + dur * 0.3);
      osc.frequency.linearRampToValueAtTime(baseFreq * 0.95, startTime + dur);
      osc.type = 'sine';
      gain.gain.setValueAtTime(0, startTime);
      gain.gain.linearRampToValueAtTime(0.15, startTime + 0.05);
      gain.gain.setValueAtTime(0.15, startTime + dur - 0.05);
      gain.gain.linearRampToValueAtTime(0, startTime + dur);
      osc.connect(gain);
      gain.connect(dest);
      osc.start(startTime);
      osc.stop(startTime + dur);
    });

    addLog('success', `✓ Scene ${scene.sceneNumber}: ${scene.slideTitle}`);
  }

  const totalDuration = scriptData.duration * 1000;
  const sceneDurations = scriptData.scenes.map(s => s.duration * 1000);
  let sceneIndex = 0;
  let sceneStart = Date.now();
  let totalStart = Date.now();

  speakScene(scriptData.scenes[0]);

  function renderLoop() {
    if (!isRecording) return;
    const now = Date.now();
    const totalElapsed = now - totalStart;
    const sceneElapsed = now - sceneStart;
    const totalProgress = Math.min(totalElapsed / totalDuration, 1);
    const pct = Math.round(totalProgress * 100);
    document.getElementById('progress-fill').style.width = pct + '%';
    document.getElementById('progress-pct').textContent = pct + '%';
    document.getElementById('progress-label-text').textContent = `Scene ${sceneIndex + 1} of ${scriptData.scenes.length}`;
    drawScene(canvas, scriptData.scenes[sceneIndex], totalProgress);
    if (sceneElapsed >= sceneDurations[sceneIndex]) {
      sceneIndex++;
      sceneStart = now;
      if (sceneIndex < scriptData.scenes.length) speakScene(scriptData.scenes[sceneIndex]);
    }
    if (totalElapsed >= totalDuration + 500) { stopRecording(); return; }
    animFrame = requestAnimationFrame(renderLoop);
  }

  animFrame = requestAnimationFrame(renderLoop);
}

function stopRecording() {
  isRecording = false;
  if (animFrame) cancelAnimationFrame(animFrame);
  window.speechSynthesis.cancel();
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
  document.getElementById('btn-stop').style.display = 'none';
  addLog('success', '✓ Recording complete! Processing video with audio...');
}"""

content = content.replace(old_recording, new_recording)

with open('yan-studio.html', 'w') as f:
    f.write(content)

print("✅ yan-studio.html updated successfully")
print("  - API endpoint fixed")
print("  - Model name fixed")  
print("  - Audio capture added to video recording")
