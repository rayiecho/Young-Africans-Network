with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

start = 821  # line 822 (0-indexed)
end = 911    # line 912 (0-indexed)

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

  const speed = parseFloat(document.getElementById('voice-speed').value);

  // Draw first scene immediately
  drawScene(canvas, scriptData.scenes[0], 0);

  // Request tab audio capture
  let tabStream = null;
  try {
    tabStream = await navigator.mediaDevices.getDisplayMedia({
      video: { displaySurface: 'browser' },
      audio: { suppressLocalAudioPlayback: false },
      preferCurrentTab: true
    });
    addLog('info', '🎤 Tab audio enabled — voice will be in video!');
  } catch(e) {
    addLog('info', '⚠ No audio capture — video will be silent.');
  }

  // Canvas stream
  const canvasStream = canvas.captureStream(30);

  // Merge canvas + tab audio if available
  let finalStream = canvasStream;
  if (tabStream) {
    const audioTracks = tabStream.getAudioTracks();
    audioTracks.forEach(track => finalStream.addTrack(track));
  }

  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus')
    ? 'video/webm;codecs=vp9,opus'
    : MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')
    ? 'video/webm;codecs=vp8,opus'
    : 'video/webm';

  mediaRecorder = new MediaRecorder(finalStream, { mimeType, videoBitsPerSecond: 2500000 });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = () => {
    if (tabStream) tabStream.getTracks().forEach(t => t.stop());
    finishVideo();
  };
  mediaRecorder.start(100);
  addLog('info', '▶ Recording started...');

  function speakScene(scene) {
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(scene.voiceover);
    utt.rate = speed; utt.pitch = 1; utt.volume = 1;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v => v.lang === 'en-GB') ||
                      voices.find(v => v.lang.startsWith('en')) || voices[0];
    if (preferred) utt.voice = preferred;
    window.speechSynthesis.speak(utt);
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

'''

lines = lines[:start] + [new_func] + lines[end:]

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)

print(f"✅ startRecording replaced successfully")
