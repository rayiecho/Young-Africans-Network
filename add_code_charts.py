with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add code/math detection and renderer to drawScene
old_color_const = 'const COLORS = {'
new_color_const = '''// ── CODE DETECTION ──
function detectSceneType(text) {
  if (!text) return 'normal';
  const codePatterns = [/```[\s\S]*```/, /def |function |class |import |const |let |var |if\(|for\(|while\(/, /\{\s*\n/, /<\w+>/, /=>/, /\(\) =>/];
  const mathPatterns = [/\d+\s*[\+\-\*\/\^]\s*\d+/, /=\s*\d/, /[∑∫∏√∞∆]/,  /equation|formula|calculate|solve|theorem/i];
  const chartPatterns = [/(\d+)%/, /increased|decreased|grew|declined|percent|ratio|compared/i, /chart|graph|data|statistics|survey/i];
  if (codePatterns.some(p => p.test(text))) return 'code';
  if (mathPatterns.some(p => p.test(text))) return 'math';
  if (chartPatterns.some(p => p.test(text))) return 'chart';
  return 'normal';
}

function extractNumbers(text) {
  const matches = text.match(/(\w[\w\s]*?):\s*(\d+(?:\.\d+)?)\s*%?/g) || [];
  const numbers = text.match(/\b(\d+(?:\.\d+)?)\s*(%|percent|million|billion|thousand)?/gi) || [];
  const result = [];
  matches.forEach(m => {
    const parts = m.match(/(.+?):\s*(\d+(?:\.\d+)?)/);
    if (parts) result.push({ label: parts[1].trim().substring(0, 12), value: parseFloat(parts[2]) });
  });
  if (!result.length && numbers.length >= 2) {
    numbers.slice(0, 5).forEach((n, i) => {
      result.push({ label: `Item ${i+1}`, value: parseFloat(n) });
    });
  }
  return result.slice(0, 6);
}

function drawCodeScene(canvas, scene, progress, currentWord = -1) {
  const ctx = canvas.getContext('2d');
  const W = canvas.width; const H = canvas.height;
  
  // Dark code editor background
  ctx.fillStyle = '#0d1117';
  ctx.fillRect(0, 0, W, H);
  
  // Editor chrome
  ctx.fillStyle = '#161b22';
  ctx.fillRect(0, 0, W, 40);
  ['#ff5f56','#ffbd2e','#27c93f'].forEach((c, i) => {
    ctx.fillStyle = c;
    ctx.beginPath(); ctx.arc(20 + i * 20, 20, 6, 0, Math.PI*2); ctx.fill();
  });
  ctx.fillStyle = 'rgba(255,255,255,0.4)';
  ctx.font = '12px Space Mono, monospace';
  ctx.textAlign = 'center';
  ctx.fillText(scene.slideTitle + '.py', W/2, 26);
  
  // YAN badge
  ctx.fillStyle = '#F5A623';
  ctx.font = 'bold 11px Space Mono, monospace';
  ctx.textAlign = 'right';
  ctx.fillText('YAN STUDIO', W - 20, 26);
  
  // Line numbers column
  ctx.fillStyle = '#21262d';
  ctx.fillRect(0, 40, 50, H - 40);
  
  // Code content
  const codeText = scene.voiceover;
  const lines = codeText.split(/[.!?]+/).filter(l => l.trim()).slice(0, 12);
  const revealedLines = Math.ceil((currentWord / Math.max(codeText.split(' ').length, 1)) * lines.length);
  
  const keywords = ['def','function','class','return','if','else','for','while','import','const','let','var','true','false','null'];
  const colors_map = { keyword: '#ff7b72', string: '#a5d6ff', number: '#79c0ff', comment: '#8b949e', default: '#e6edf3' };
  
  lines.forEach((line, i) => {
    if (i > revealedLines) return;
    const y = 80 + i * 36;
    
    // Line number
    ctx.fillStyle = '#484f58';
    ctx.font = '13px Space Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText(i + 1, 42, y);
    
    // Code line with basic syntax highlighting
    const words = line.trim().split(' ');
    let x = 65;
    words.forEach(word => {
      let color = colors_map.default;
      if (keywords.includes(word.toLowerCase())) color = colors_map.keyword;
      else if (word.startsWith('"') || word.startsWith("'")) color = colors_map.string;
      else if (/^\d+/.test(word)) color = colors_map.number;
      else if (word.startsWith('#')) color = colors_map.comment;
      
      ctx.fillStyle = color;
      ctx.font = i === revealedLines ? 'bold 15px Space Mono, monospace' : '14px Space Mono, monospace';
      ctx.textAlign = 'left';
      ctx.fillText(word, x, y);
      x += ctx.measureText(word + ' ').width;
    });
    
    // Cursor on current line
    if (i === revealedLines) {
      ctx.fillStyle = '#F5A623';
      ctx.fillRect(x + 2, y - 14, 2, 18);
    }
  });
  
  // Progress bar
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  ctx.fillRect(0, H-4, W, 4);
  ctx.fillStyle = '#F5A623';
  ctx.fillRect(0, H-4, W * progress, 4);
}

function drawChartScene(canvas, scene, progress, currentWord = -1) {
  const ctx = canvas.getContext('2d');
  const W = canvas.width; const H = canvas.height;
  const colors = ['#F5A623','#74C69D','#4CC9F0','#F72585','#7209B7','#3A0CA3'];
  
  // Background
  ctx.fillStyle = '#0A1628';
  ctx.fillRect(0, 0, W, H);
  
  // Grid
  ctx.strokeStyle = 'rgba(245,166,35,0.05)';
  ctx.lineWidth = 1;
  for (let x = 0; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
  for (let y = 0; y < H; y += 60) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }
  
  // Title
  ctx.fillStyle = '#F8F9FC';
  ctx.font = `bold ${W > 800 ? 36 : 28}px Syne, sans-serif`;
  ctx.textAlign = 'center';
  ctx.fillText(scene.slideTitle, W/2, 60);
  
  ctx.fillStyle = '#F5A623';
  ctx.font = '16px Syne, sans-serif';
  ctx.fillText(scene.slideSubtitle, W/2, 90);
  
  // Extract data
  const data = extractNumbers(scene.voiceover);
  if (!data.length) {
    // Fallback - show text
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.font = '18px Syne, sans-serif';
    wrapText(ctx, scene.voiceover, W/2, H/2, W*0.8, 28);
    return;
  }
  
  const maxVal = Math.max(...data.map(d => d.value));
  const chartH = H * 0.45;
  const chartY = H * 0.88;
  const barW = Math.min((W * 0.7) / data.length - 20, 100);
  const startX = (W - (data.length * (barW + 20))) / 2;
  const animProgress = Math.min(progress * 2, 1);
  
  data.forEach((d, i) => {
    const barH = (d.value / maxVal) * chartH * animProgress;
    const x = startX + i * (barW + 20);
    const y = chartY - barH;
    
    // Bar
    const grad = ctx.createLinearGradient(x, y, x, chartY);
    grad.addColorStop(0, colors[i % colors.length]);
    grad.addColorStop(1, colors[i % colors.length] + '44');
    ctx.fillStyle = grad;
    roundRect(ctx, x, y, barW, barH, 6);
    ctx.fill();
    
    // Value label
    ctx.fillStyle = '#F8F9FC';
    ctx.font = 'bold 16px Syne, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(d.value + (scene.voiceover.includes('%') ? '%' : ''), x + barW/2, y - 10);
    
    // Category label
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.font = '12px Syne, sans-serif';
    ctx.fillText(d.label, x + barW/2, chartY + 20);
  });
  
  // YAN branding
  ctx.fillStyle = '#F5A623';
  ctx.font = 'bold 11px Space Mono, monospace';
  ctx.textAlign = 'left';
  ctx.fillText('YAN STUDIO', 20, H - 15);
  
  // Progress bar
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  ctx.fillRect(0, H-4, W, 4);
  ctx.fillStyle = '#F5A623';
  ctx.fillRect(0, H-4, W * progress, 4);
}

const COLORS = {'''

content = content.replace(old_color_const, new_color_const, 1)

# 2. Wire code/chart detection into drawScene
old_style_check = "  if (style === 'whiteboard') { drawWhiteboardScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }"
new_style_check = """  // Auto-detect scene type for smart rendering
  const sceneType = detectSceneType((scene.voiceover || '') + ' ' + (scene.slideTitle || ''));
  if (style === 'slides' && sceneType === 'code') { drawCodeScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }
  if (style === 'slides' && sceneType === 'chart') { drawChartScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }
  if (style === 'whiteboard') { drawWhiteboardScene(canvas, scene, progress, currentWord); applyTransition(canvas); return; }"""

content = content.replace(old_style_check, new_style_check, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Code renderer + Chart generator added!")
