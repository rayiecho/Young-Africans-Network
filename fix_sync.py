with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

# Fix 1: Word timing - sync with actual audio duration
for i, line in enumerate(lines):
    if 'const timePerWord = (scene.duration * 1000) / words.length;' in line:
        lines[i] = '''        // Sync word timing with actual audio - voice speaks at ~2.5 words/sec
        const wordsPerSecond = 2.5;
        const timePerWord = 1000 / wordsPerSecond;\n'''
        print(f"✅ Word timing fixed at line {i+1}")
        break

# Fix 2: Move word reveal to TOP of slide not bottom
for i, line in enumerate(lines):
    if '// Rolling text reveal - top to bottom, scrolls when full' in line:
        start = i
        depth = 0
        end = i
        for j in range(i, min(i + 80, len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            end = j
            if j > i + 5 and depth <= 0:
                break
        
        new_block = '''  // Rolling text reveal - TOP of slide, scrolls down then up
  if (scene.voiceover && currentWord >= 0) {
    const words = scene.voiceover.split(' ');
    const wordsPerLine = 5;
    const lineHeight = 44;
    const maxVisibleLines = Math.floor((H * 0.78) / lineHeight);
    const topPadding = 85;

    // Group into lines
    const allLines = [];
    for (let wi = 0; wi < words.length; wi += wordsPerLine) {
      allLines.push(words.slice(wi, wi + wordsPerLine));
    }

    // Which line is currently being spoken
    const currentLine = Math.floor(currentWord / wordsPerLine);

    // Scroll so current line is always visible - keep it near bottom of visible area
    const scrollOffset = Math.max(0, currentLine - maxVisibleLines + 2);
    const visibleLines = allLines.slice(scrollOffset, scrollOffset + maxVisibleLines);

    visibleLines.forEach((lineWords, visIdx) => {
      const actualLineIdx = visIdx + scrollOffset;
      const y = topPadding + visIdx * lineHeight;
      const lineStartWord = actualLineIdx * wordsPerLine;

      let x = W * 0.05;
      lineWords.forEach((word, wordIdx) => {
        const globalIdx = lineStartWord + wordIdx;
        if (globalIdx > currentWord) return;

        const isActive = globalIdx === currentWord;
        const lineFade = Math.max(0.25, 1 - (currentLine - actualLineIdx) * 0.2);

        ctx.globalAlpha = isActive ? 1 : lineFade;
        ctx.shadowColor = isActive ? colors.accent : 'transparent';
        ctx.shadowBlur = isActive ? 14 : 0;
        ctx.fillStyle = isActive ? colors.accent : colors.text;
        ctx.font = `bold ${isActive ? 32 : 28}px Syne, sans-serif`;
        ctx.textAlign = 'left';
        ctx.fillText(word, x, y);
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;
        x += ctx.measureText(word + ' ').width + 4;
      });
    });
  }
'''
        lines[start:end+1] = [new_block]
        print(f"✅ Rolling reveal fixed at line {start+1}")
        break

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)
print("Done")
