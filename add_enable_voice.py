with open('yan-studio.html', 'r') as f:
    content = f.read()

old = 'async function startRecording() {'

new = '''let tabStream = null;

async function enableVoice() {
  try {
    tabStream = await navigator.mediaDevices.getDisplayMedia({
      video: { displaySurface: "browser" },
      audio: true,
      preferCurrentTab: true
    });
    document.getElementById("btn-record").style.display = "none";
    document.getElementById("btn-record-go").style.display = "inline-flex";
    addLog("success", "🎤 Voice enabled! Now click Start Recording.");
  } catch(e) {
    addLog("error", "⚠ Voice not enabled. Click Enable Voice First and allow tab audio.");
    document.getElementById("btn-record-go").style.display = "inline-flex";
  }
}

async function startRecording() {'''

content = content.replace(old, new)

# Remove tabStream declaration inside startRecording since it's now global
content = content.replace(
    '  // Request tab audio capture\n  let tabStream = null;\n',
    '  // Use global tabStream from enableVoice\n'
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ enableVoice function added")
