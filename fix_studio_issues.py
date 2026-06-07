with open('yan-studio.html', 'r') as f:
    content = f.read()

# Fix 1: Faster transition
content = content.replace(
    'const TRANSITION_DURATION = 500; // ms',
    'const TRANSITION_DURATION = 200; // ms'
)

# Fix 2: Stronger voice - use different Cloudflare voice
content = content.replace(
    "body: JSON.stringify({ text: scene.voiceover, voice: 'asteria' })",
    "body: JSON.stringify({ text: scene.voiceover, voice: 'orion', speed: 1.1 })"
)

# Fix 3: Progressive text reveal - replace subtitle system with top-to-bottom word reveal
old_subtitle = '''  // Karaoke subtitles
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
  }'''

new_subtitle = '''  // Progressive text reveal - words appear top to bottom as spoken
  if (scene.voiceover && currentWord >= 0) {
    const words = scene.voiceover.split(' ');
    const wordsPerLine = 6;
    const lineHeight = 34;
    const startY = H * 0.15;
    const maxLines = Math.floor((H * 0.75) / lineHeight);
    
    // Group words into lines
    const lines = [];
    for (let i = 0; i < words.length; i += wordsPerLine) {
      lines.push(words.slice(i, i + wordsPerLine));
    }
    
    // Dark overlay for text area
    ctx.fillStyle = 'rgba(0,0,0,0.45)';
    ctx.fillRect(W * 0.05, startY - 10, W * 0.9, Math.min(lines.length, maxLines) * lineHeight + 20);
    
    // Draw each line progressively
    lines.forEach((lineWords, lineIdx) => {
      if (lineIdx >= maxLines) return;
      const y = startY + lineIdx * lineHeight;
      const lineStartWord = lineIdx * wordsPerLine;
      
      let x = W * 0.08;
      lineWords.forEach((word, wordIdx) => {
        const globalWordIdx = lineStartWord + wordIdx;
        const isActive = globalWordIdx === currentWord;
        const isRevealed = globalWordIdx <= currentWord;
        
        if (!isRevealed) return; // Don't show future words
        
        if (isActive) {
          ctx.fillStyle = colors.accent;
          ctx.font = 'bold 26px Syne, sans-serif';
          // Glow effect on active word
          ctx.shadowColor = colors.accent;
          ctx.shadowBlur = 12;
        } else {
          ctx.fillStyle = 'rgba(255,255,255,0.9)';
          ctx.font = 'bold 24px Syne, sans-serif';
          ctx.shadowBlur = 0;
        }
        
        ctx.textAlign = 'left';
        ctx.fillText(word, x, y + 24);
        ctx.shadowBlur = 0;
        x += ctx.measureText(word + ' ').width + 4;
      });
    });
  }'''

content = content.replace(old_subtitle, new_subtitle, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ All 3 issues fixed!")
