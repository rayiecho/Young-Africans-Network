with open('yan-studio.html', 'r') as f:
    content = f.read()

# Wrap main title drawing with condition - only show if no words revealed yet
content = content.replace(
    '''  // Main title
  const titleY = H * 0.42;
  ctx.fillStyle = colors.text;
  ctx.font = `bold ${W > 800 ? 48 : 36}px Syne, sans-serif`;
  ctx.textAlign = 'center';
  wrapText(ctx, scene.slideTitle, W/2, titleY, W*0.8, W > 800 ? 58 : 44);

  // Subtitle
  ctx.fillStyle = colors.accent;
  ctx.font = `${W > 800 ? 22 : 18}px Syne, sans-serif`;
  wrapText(ctx, scene.slideSubtitle, W/2, H * 0.62, W*0.7, W > 800 ? 30 : 26);

  // Decorative line
  ctx.strokeStyle = colors.accent;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(W/2 - 40, H * 0.72);
  ctx.lineTo(W/2 + 40, H * 0.72);
  ctx.stroke();

  // Bottom tag
  ctx.fillStyle = \'rgba(245,166,35,0.1)\';
  roundRect(ctx, W/2 - 100, H*0.78, 200, 32, 16);
  ctx.fill();
  ctx.fillStyle = colors.accent;
  ctx.font = \'11px Space Mono, monospace\';
  ctx.textAlign = \'center\';
  ctx.fillText(\'BUILDING THE FUTURE, TOGETHER\', W/2, H*0.78 + 20);''',

    '''  // Show title small at top, rolling text takes main area
  if (currentWord < 0) {
    // No words yet - show full title centered
    const titleY = H * 0.42;
    ctx.fillStyle = colors.text;
    ctx.font = `bold ${W > 800 ? 48 : 36}px Syne, sans-serif`;
    ctx.textAlign = 'center';
    wrapText(ctx, scene.slideTitle, W/2, titleY, W*0.8, W > 800 ? 58 : 44);
    ctx.fillStyle = colors.accent;
    ctx.font = `${W > 800 ? 22 : 18}px Syne, sans-serif`;
    wrapText(ctx, scene.slideSubtitle, W/2, H * 0.62, W*0.7, W > 800 ? 30 : 26);
    ctx.strokeStyle = colors.accent;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(W/2 - 40, H * 0.72);
    ctx.lineTo(W/2 + 40, H * 0.72);
    ctx.stroke();
  } else {
    // Words revealing - show small title at very top
    ctx.fillStyle = colors.accent;
    ctx.font = 'bold 15px Space Mono, monospace';
    ctx.textAlign = 'left';
    ctx.fillText(scene.slideTitle.toUpperCase(), W * 0.05, 78);
  }

  // Bottom tag always visible
  ctx.fillStyle = \'rgba(245,166,35,0.1)\';
  roundRect(ctx, W/2 - 100, H*0.91, 200, 28, 14);
  ctx.fill();
  ctx.fillStyle = colors.accent;
  ctx.font = \'10px Space Mono, monospace\';
  ctx.textAlign = \'center\';
  ctx.fillText(\'BUILDING THE FUTURE, TOGETHER\', W/2, H*0.91 + 18);'''
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Text overlap fixed!")
