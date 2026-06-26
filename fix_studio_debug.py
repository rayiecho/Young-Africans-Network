with open('yan-studio.html', 'r') as f:
    content = f.read()

old = '''  } catch (err) {
    document.getElementById('loading-script').style.display = 'none';
    document.querySelector('#panel-1 .card').style.display = 'block';
    addLog('error', '✗ Failed to generate script. Check your connection and try again.');
    alert('Script generation failed. Please try again.');
  }'''

new = '''  } catch (err) {
    document.getElementById('loading-script').style.display = 'none';
    document.querySelector('#panel-1 .card').style.display = 'block';
    addLog('error', '✗ Error: ' + err.message);
    alert('Error: ' + err.message);
  }'''

updated = content.replace(old, new)

with open('yan-studio.html', 'w') as f:
    f.write(updated)
print("✅ Debug logging added")
