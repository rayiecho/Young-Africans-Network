with open('yan-studio.html', 'r') as f:
    content = f.read()

old = '''  mediaRecorder = new MediaRecorder(canvasStream, { mimeType, videoBitsPerSecond: 2500000 });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = finishVideo;
  mediaRecorder.start(100);

  addLog('info', '▶ Recording started with audio...');'''

new = '''  mediaRecorder = new MediaRecorder(canvasStream, { mimeType, videoBitsPerSecond: 2500000 });
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };
  mediaRecorder.onstop = finishVideo;

  // Draw first frame before starting recording
  drawScene(canvas, scriptData.scenes[0], 0);
  
  // Small delay to ensure canvas is ready
  await new Promise(resolve => setTimeout(resolve, 500));
  
  mediaRecorder.start(100);
  addLog('info', '▶ Recording started with audio...');'''

content = content.replace(old, new)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Recording delay fix applied")
