with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Update drawScene to accept currentWord parameter
old = 'function drawScene(canvas, scene, progress) {'
new = 'function drawScene(canvas, scene, progress, currentWord = -1) {'

content = content.replace(old, new, 1)

# 2. Add subtitle rendering at end of drawScene (before closing brace after bottom tag)
old2 = "  ctx.fillStyle = colors.accent;\n  ctx.font = '11px Space Mono, monospace';\n  ctx.textAlign = 'center';\n  ctx.fillText('BUILDING THE FUTURE, TOGETHER', W/2, H*0.78 + 20);"

new2 = """  ctx.fillStyle = colors.accent;
  ctx.font = '11px Space Mono, monospace';
  ctx.textAlign = 'center';
  ctx.fillText('BUILDING THE FUTURE, TOGETHER', W/2, H*0.78 + 20);

  // Karaoke subtitles
  if (scene.voiceover) {
    const words = scene.voiceover.split(' ');
    const subtitleY = H * 0.91;
    const subtitleBgH = 52;
    
    // Subtitle background
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(0, subtitleY - subtitleBgH/2, W, subtitleBgH);
    
    // Show current line (5 words at a time)
    const wordsPerLine = 7;
    const lineIndex = currentWord >= 0 ? Math.floor(currentWord / wordsPerLine) : 0;
    const lineStart = lineIndex * wordsPerLine;
    const lineWords = words.slice(lineStart, lineStart + wordsPerLine);
    const currentWordInLine = currentWord - lineStart;
    
    // Calculate total line width to center it
    ctx.font = 'bold 22px Syne, sans-serif';
    let totalWidth = 0;
    lineWords.forEach((w, i) => {
      totalWidth += ctx.measureText(w + ' ').width;
    });
    
    let x = W/2 - totalWidth/2;
    lineWords.forEach((word, i) => {
      const isActive = i === currentWordInLine;
      const isPast = i < currentWordInLine;
      
      if (isActive) {
        ctx.fillStyle = colors.accent; // Gold for current word
        ctx.font = 'bold 24px Syne, sans-serif';
      } else if (isPast) {
        ctx.fillStyle = 'rgba(255,255,255,0.5)'; // Dim for past words
        ctx.font = 'bold 22px Syne, sans-serif';
      } else {
        ctx.fillStyle = 'rgba(255,255,255,0.85)'; // White for upcoming
        ctx.font = 'bold 22px Syne, sans-serif';
      }
      
      ctx.textAlign = 'left';
      ctx.fillText(word, x, subtitleY + 8);
      x += ctx.measureText(word + ' ').width;
    });
  }"""

content = content.replace(old2, new2, 1)

# 3. Add currentWord tracking in startRecording
old3 = '  drawScene(canvas, scriptData.scenes[0], 0);'
new3 = '  window.currentWord = 0;\n  window.wordTimer = null;\n  drawScene(canvas, scriptData.scenes[0], 0, 0);'

content = content.replace(old3, new3, 1)

# 4. Update renderLoop to pass currentWord
old4 = '    drawScene(canvas, scriptData.scenes[sceneIndex], totalProgress);'
new4 = '    drawScene(canvas, scriptData.scenes[sceneIndex], totalProgress, window.currentWord || 0);'

content = content.replace(old4, new4, 1)

# 5. Update playSceneAudio to track word timing
old5 = '''  async function playSceneAudio(index) {
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
  }'''

new5 = '''  async function playSceneAudio(index) {
    if (!audioBuffers[index]) return;
    try {
      const decoded = await audioCtx.decodeAudioData(audioBuffers[index].slice(0));
      const source = audioCtx.createBufferSource();
      source.buffer = decoded;
      source.connect(dest);
      source.connect(audioCtx.destination);
      source.start();

      // Word-by-word karaoke timing
      const scene = scriptData.scenes[index];
      const words = scene.voiceover.split(' ');
      const timePerWord = (scene.duration * 1000) / words.length;
      window.currentWord = 0;
      if (window.wordTimer) clearInterval(window.wordTimer);
      window.wordTimer = setInterval(() => {
        window.currentWord++;
        if (window.currentWord >= words.length) {
          clearInterval(window.wordTimer);
        }
      }, timePerWord);

    } catch(e) {
      addLog('error', 'Audio decode error: ' + e.message);
    }
  }'''

content = content.replace(old5, new5, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)

print("✅ Karaoke subtitles added!")
