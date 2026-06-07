with open('yan-studio.html', 'r') as f:
    content = f.read()

# Find and replace the broken recording setup
old = '''  // AudioContext for capturing audio into video
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

  // Draw first frame before recording
  drawScene(canvas, scriptData.scenes[0], 0);
  await new Promise(resolve => setTimeout(resolve, 300));

  mediaRecorder.start(100);
  addLog('info', '▶ Recording started with audio...');'''

new = '''  // Canvas stream only - stable recording
  const canvasStream = canvas.captureStream(30);
  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
    ? 'video/webm;codecs=vp9'
    : 'video/webm';

  mediaRecorder = new MediaRecorder(canvasStream, { mimeType, videoBitsPerSecond: 2500000 });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = finishVideo;
  mediaRecorder.start(100);
  addLog('info', '▶ Recording started...');'''

if old in content:
    content = content.replace(old, new)
    print("✅ Reverted to stable video-only recording")
else:
    print("❌ Pattern not found")

with open('yan-studio.html', 'w') as f:
    f.write(content)
