with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

# Remove the unused AudioContext lines (857-858)
new_lines = []
skip_next = False
for i, line in enumerate(lines):
    # Remove unused audioCtx and dest lines
    if '// Audio Context for capturing speech' in line:
        continue
    if 'const audioCtx = new (window.AudioContext' in line and 'canvasStream' not in lines[i-5]:
        continue
    if 'const dest = audioCtx.createMediaStreamDestination()' in line:
        continue
    # Fix mimeType to be more compatible
    if "const mimeType = 'video/webm';" in line:
        line = "  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : MediaRecorder.isTypeSupported('video/webm') ? 'video/webm' : '';\n"
    new_lines.append(line)

with open('yan-studio.html', 'w') as f:
    f.writelines(new_lines)

print("✅ Fixed mimeType and removed unused AudioContext")
