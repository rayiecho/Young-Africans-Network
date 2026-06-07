with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

new_block = '''  // Rolling text reveal - top to bottom, scrolls when full
  if (scene.voiceover && currentWord >= 0) {
    const words = scene.voiceover.split(' ');
    const wordsPerLine = 5;
    const lineHeight = 42;
    const maxVisibleLines = Math.floor((H * 0.72) / lineHeight);
    const startY = 100;
    
    // Group into lines
    const allLines = [];
    for (let i = 0; i < words.length; i += wordsPerLine) {
      allLines.push(words.slice(i, i + wordsPerLine));
    }
    
    // Current line being spoken
    const currentLine = Math.floor(currentWord / wordsPerLine);
    
    // Scroll offset - keep current line visible
    const scrollOffset = Math.max(0, currentLine - maxVisibleLines + 2);
    const visibleLines = allLines.slice(scrollOffset, scrollOffset + maxVisibleLines);
    
    visibleLines.forEach((lineWords, visIdx) => {
      const actualLineIdx = visIdx + scrollOffset;
      const y = startY + visIdx * lineHeight;
      const lineStartWord = actualLineIdx * wordsPerLine;
      
      let x = W * 0.06;
      lineWords.forEach((word, wordIdx) => {
        const globalIdx = lineStartWord + wordIdx;
        if (globalIdx > currentWord) return; // not yet spoken
        
        const isActive = globalIdx === currentWord;
        const isCurrent = actualLineIdx === currentLine;
        
        // Fade old lines
        const lineFade = Math.max(0.3, 1 - (currentLine - actualLineIdx) * 0.15);
        
        ctx.shadowColor = isActive ? colors.accent : 'transparent';
        ctx.shadowBlur = isActive ? 12 : 0;
        ctx.globalAlpha = isActive ? 1 : lineFade;
        ctx.fillStyle = isActive ? colors.accent : colors.text;
        ctx.font = `bold ${isActive ? 30 : 27}px Syne, sans-serif`;
        ctx.textAlign = 'left';
        ctx.fillText(word, x, y);
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;
        x += ctx.measureText(word + ' ').width + 3;
      });
    });
  }
'''

# Find and replace the word reveal block
for i, line in enumerate(lines):
    if '// Progressive text reveal - words appear top to bottom as spoken' in line or \
       '// Progressive text reveal - words appear top to bottom' in line or \
       '// Rolling text reveal' in line:
        start = i
        # Find end of block
        depth = 0
        end = i
        for j in range(i, min(i + 80, len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            end = j
            if j > i + 5 and depth <= 0:
                break
        lines[start:end+1] = [new_block]
        print(f"✅ Rolling text reveal fixed at line {start+1}")
        break

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)
print("Done")
