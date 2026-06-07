import os

favicon_line = '  <link rel="icon" type="image/jpeg" href="https://youngafricansnetwork.org/images/logo.jpeg">\n'

files = [f for f in os.listdir('.') if f.endswith('.html')]

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    if favicon_line.strip() not in content:
        updated = content.replace('<head>', '<head>\n' + favicon_line, 1)
        with open(f, 'w') as file:
            file.write(updated)
        print(f"✅ Updated {f}")
    else:
        print(f"⏭️ Already has favicon: {f}")
