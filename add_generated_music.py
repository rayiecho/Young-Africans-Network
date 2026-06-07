with open('yan-studio.html', 'r') as f:
    content = f.read()

old = '''const MUSIC_URLS = {
  inspirational: 'https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3',
  upbeat: null,
  calm: null,
  corporate: null
};'''

new = '''// ── GENERATED BACKGROUND MUSIC ──
function startBackgroundMusic(audioCtx, dest, style, duration) {
  const musicType = document.getElementById('bg-music') ? 
    document.getElementById('bg-music').value : 'none';
  if (musicType === 'none') return null;

  const nodes = [];
  const endTime = audioCtx.currentTime + duration;

  if (musicType === 'inspirational') {
    // African-inspired: warm bass drone + gentle percussion rhythm
    const bpm = 80;
    const beat = 60 / bpm;
    for (let t = audioCtx.currentTime; t < endTime; t += beat) {
      // Kick drum
      const kick = audioCtx.createOscillator();
      const kickGain = audioCtx.createGain();
      kick.frequency.setValueAtTime(120, t);
      kick.frequency.exponentialRampToValueAtTime(40, t + 0.1);
      kickGain.gain.setValueAtTime(0.3, t);
      kickGain.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
      kick.connect(kickGain); kickGain.connect(dest);
      kick.start(t); kick.stop(t + 0.15);

      // Hi-hat on off-beats
      const hat = audioCtx.createOscillator();
      const hatGain = audioCtx.createGain();
      hat.type = 'square';
      hat.frequency.value = 8000;
      hatGain.gain.setValueAtTime(0.05, t + beat/2);
      hatGain.gain.exponentialRampToValueAtTime(0.001, t + beat/2 + 0.05);
      hat.connect(hatGain); hatGain.connect(dest);
      hat.start(t + beat/2); hat.stop(t + beat/2 + 0.05);
    }
    // Warm drone
    const drone = audioCtx.createOscillator();
    const droneGain = audioCtx.createGain();
    drone.type = 'sine';
    drone.frequency.value = 55;
    droneGain.gain.setValueAtTime(0.08, audioCtx.currentTime);
    drone.connect(droneGain); droneGain.connect(dest);
    drone.start(audioCtx.currentTime); drone.stop(endTime);

  } else if (musicType === 'upbeat') {
    // Upbeat: faster tempo, higher energy
    const bpm = 120;
    const beat = 60 / bpm;
    for (let t = audioCtx.currentTime; t < endTime; t += beat) {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.value = [220, 277, 330, 440][Math.floor((t * 2) % 4)];
      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + beat * 0.8);
      osc.connect(gain); gain.connect(dest);
      osc.start(t); osc.stop(t + beat * 0.8);
    }

  } else if (musicType === 'calm') {
    // Calm: slow breathing pad
    const pad = audioCtx.createOscillator();
    const padGain = audioCtx.createGain();
    pad.type = 'sine';
    pad.frequency.value = 174;
    padGain.gain.setValueAtTime(0, audioCtx.currentTime);
    padGain.gain.linearRampToValueAtTime(0.06, audioCtx.currentTime + 2);
    padGain.gain.linearRampToValueAtTime(0.04, endTime - 2);
    padGain.gain.linearRampToValueAtTime(0, endTime);
    pad.connect(padGain); padGain.connect(dest);
    pad.start(audioCtx.currentTime); pad.stop(endTime);

    const pad2 = audioCtx.createOscillator();
    const pad2Gain = audioCtx.createGain();
    pad2.type = 'sine';
    pad2.frequency.value = 261;
    pad2Gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
    pad2.connect(pad2Gain); pad2Gain.connect(dest);
    pad2.start(audioCtx.currentTime); pad2.stop(endTime);

  } else if (musicType === 'corporate') {
    // Corporate: clean, minimal
    const bpm = 100;
    const beat = 60 / bpm;
    const notes = [261, 329, 392, 523];
    let ni = 0;
    for (let t = audioCtx.currentTime; t < endTime; t += beat * 2) {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.value = notes[ni % notes.length];
      gain.gain.setValueAtTime(0.08, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + beat * 1.8);
      osc.connect(gain); gain.connect(dest);
      osc.start(t); osc.stop(t + beat * 1.8);
      ni++;
    }
  }

  return nodes;
}'''

content = content.replace(old, new, 1)

# Wire music into startRecording
old_music_call = "  addLog('info', '🎤 Generating voiceover audio...');"
new_music_call = "  addLog('info', '🎤 Generating voiceover audio...');\n  // Music will start after AudioContext is set up"

content = content.replace(old_music_call, new_music_call, 1)

# Start music after AudioContext setup
old_audio_setup = "  addLog('info', '▶ Recording video with voice...');"
new_audio_setup = "  // Start background music\n  startBackgroundMusic(audioCtx, dest, document.getElementById('bg-music').value, scriptData.duration);\n  addLog('info', '▶ Recording video with voice...');"

content = content.replace(old_audio_setup, new_audio_setup, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Generated background music added!")
