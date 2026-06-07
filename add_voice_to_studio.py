with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

# Find startRecording function
start = None
end = None
for i, line in enumerate(lines):
    if 'async function startRecording()' in line:
        start = i
    if start and 'function stopRecording()' in line:
        end = i
        break

new_func = '''async function startRecording() {
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

  addLog('info', '🎤 Generating voiceover audio...');

  // Generate all scene audio first
  const audioBuffers = [];
  for (let i = 0; i < scriptData.scenes.length; i++) {
    const scene = scriptData.scenes[i];
    try {
      const res = await fetch('https://yan-studio-worker.youngafricansn.workers.dev/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: scene.voiceover, voice: 'asteria' })
      });
      const blob = await res.blob();
      const arrayBuffer = await blob.arrayBuffer();
      audioBuffers.push(arrayBuffer);
      addLog('success', `✓ Audio generated: Scene ${scene.sceneNumber}`);
    } catch(e) {
      audioBuffers.push(null);
      addLog('error', `✗ Audio failed: Scene ${scene.sceneNumber}`);
    }
  }

  // Setup AudioContext
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const dest = audioCtx.createMediaStreamDestination();

  // Setup canvas stream + audio
  const canvasStream = canvas.captureStream(30);
  canvasStream.addTrack(dest.stream.getAudioTracks()[0]);

  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus')
    ? 'video/webm;codecs=vp9,opus'
    : 'video/webm';

  mediaRecorder = new MediaRecorder(canvasStream, { mimeType, videoBitsPerSecond: 2500000 });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = finishVideo;
  mediaRecorder.start(100);

  addLog('info', '▶ Recording video with voice...');

  const totalDuration = scriptData.duration * 1000;
  const sceneDurations = scriptData.scenes.map(s => s.duration * 1000);
  let sceneIndex = 0;
  let sceneStart = Date.now();
  let totalStart = Date.now();

  // Play audio for first scene
  async function playSceneAudio(index) {
    if (!audioBuffers[index]) return;
    try {
      const decoded = await audioCtx.decodeAudioData(audioBuffers[index].slice(0));
      const source = audioCtx.createBufferSource();
      source.buffer = decoded;
      source.connect(dest);
      source.connect(audioCtx.destination);
      source.start();
    } catch(e) {
      addLog('error', 'Audio decode error: ' + e.message);
    }
  }

  drawScene(canvas, scriptData.scenes[0], 0);
  playSceneAudio(0);

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
      if (sceneIndex < scriptData.scenes.length) {
        playSceneAudio(sceneIndex);
      }
    }
    if (totalElapsed >= totalDuration + 500) { stopRecording(); return; }
    animFrame = requestAnimationFrame(renderLoop);
  }

  animFrame = requestAnimationFrame(renderLoop);
}

'''

if start and end:
    lines = lines[:start] + [new_func] + lines[end:]
    with open('yan-studio.html', 'w') as f:
        f.writelines(lines)
    print(f"✅ Voice recording added (lines {start+1} to {end+1})")
else:
    print(f"❌ Not found. start={start}, end={end}")
