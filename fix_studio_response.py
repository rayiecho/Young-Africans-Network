with open('yan-studio.html', 'r') as f:
    content = f.read()

old = '''    const data = await response.json();
    const text = data.content[0].text.trim();
    const clean = text.replace(/```json|```/g, '').trim();
    scriptData = JSON.parse(clean);'''

new = '''    const data = await response.json();
    console.log('Worker response:', JSON.stringify(data));
    
    // Handle different response formats
    let text = '';
    if (data.content && data.content[0]) {
      text = data.content[0].text.trim();
    } else if (data.result && data.result.content) {
      text = data.result.content[0].text.trim();
    } else if (data.response) {
      text = data.response.trim();
    } else if (data.text) {
      text = data.text.trim();
    } else {
      throw new Error('Unexpected response: ' + JSON.stringify(data).substring(0, 200));
    }
    
    const clean = text.replace(/```json|```/g, '').trim();
    scriptData = JSON.parse(clean);'''

updated = content.replace(old, new)

with open('yan-studio.html', 'w') as f:
    f.write(updated)
print("✅ Response parsing fixed")
