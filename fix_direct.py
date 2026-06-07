with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

# Find the line with "Setup MediaRecorder"
start = None
end = None
for i, line in enumerate(lines):
    if '// Setup MediaRecorder' in line:
        start = i
    if start and 'Recording started' in line:
        end = i
        break

if start and end:
    print(f"✅ Found section at lines {start+1} to {end+1}")
    new_lines = [
        "  // Simple stable canvas-only recording\n",
        "  const canvasStream = canvas.captureStream(30);\n",
        "  const mimeType = 'video/webm';\n",
        "  mediaRecorder = new MediaRecorder(canvasStream, { mimeType, videoBitsPerSecond: 2500000 });\n",
        "  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) recordedChunks.push(e.data); };\n",
        "  mediaRecorder.onstop = finishVideo;\n",
        "  mediaRecorder.start(100);\n",
        "  addLog('info', '▶ Recording started...');\n",
    ]
    lines = lines[:start] + new_lines + lines[end+1:]
    with open('yan-studio.html', 'w') as f:
        f.writelines(lines)
    print("✅ File updated successfully")
else:
    print(f"❌ Section not found. start={start}, end={end}")
