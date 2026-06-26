with open('yan-studio.html', 'r') as f:
    content = f.read()

# Replace the speakScene function and recording setup
old = '''  // Speech synthesis
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

  speakScene(scriptData.scenes[0]);'''

new = '''  // Audio Context for capturing speech
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const dest = audioCtx.createMediaStreamDestination();
  const speed = parseFloat(document.getElementById('voice-speed').value);

  function speakScene(scene) {
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(scene.voiceover);
    utt.rate = speed;
    utt.pitch = 1;
    utt.volume = 1;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v => v.lang === 'en-GB') || voices.find(v => v.lang.startsWith('en')) || voices[0];
    if (preferred) utt.voice = preferred;
    window.speechSynthesis.speak(utt);
    addLog('success', `✓ Scene ${scene.sceneNumber}: ${scene.slideTitle}`);
  }

  speakScene(scriptData.scenes[0]);'''

content = content.replace(old, new)

# Fix the stream to include audio
old2 = '''  const stream = canvas.captureStream(30);
  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
  mediaRecorder = new MediaRecorder(stream, { mimeType, videoBitsPerSecond: 2500000 });'''

new2 = '''  // Capture canvas + system audio
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
  mediaRecorder = new MediaRecorder(finalStream, { mimeType, videoBitsPerSecond: 2500000 });'''

content = content.replace(old2, new2)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Voice capture fix applied")
