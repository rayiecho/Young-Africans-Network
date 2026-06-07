with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

# Find the btn-row in panel 3 and add Enable Voice button
for i, line in enumerate(lines):
    if '▶ Start Recording' in line:
        lines[i] = lines[i].replace(
            '▶ Start Recording',
            '🎤 Enable Voice First'
        ).replace(
            'onclick="startRecording()"',
            'onclick="enableVoice()"'
        )
        # Add Start Recording as second button
        lines[i] = lines[i] + '          <button class="btn btn-gold" id="btn-record-go" onclick="startRecording()" style="display:none;">▶ Start Recording</button>\n'
        break

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)
print("✅ Enable Voice button added")
