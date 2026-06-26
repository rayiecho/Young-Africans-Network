with open('yan-studio.html', 'r') as f:
    content = f.read()

old = '''  // Setup MediaRecorder
  // Capture canvas + system audio
  const canvasStream = canvas.captureStream(30);
  
  // Try to capture tab audio
  let finalStream = canvasStream;
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const dest = audioCtx.createMediaStreamDestination();
    finalStream = new MediaStream([...canvasStream.getTracks(), ...dest.stream.getTracks()]);
  } catch(e) {}
  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus') 
    ? 'video/webm;codecs=vp9,opus' 
    : MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')
    ? 'video/webm;codecs=vp8,opus'
    : 'video/webm';
  mediaRecorder = new MediaRecorder(finalStream, { mimeType, videoBitsPerSecond: 2500000 });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = finishVideo;
  mediaRecorder.start(100);
  addLog('info', '▶ Recording started...');'''

new = '''  // Simple stable canvas-only recording
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
    print("✅ Fixed!")
else:
    print("❌ Not found")

with open('yan-studio.html', 'w') as f:
    f.write(content)
