with open('yan-studio.html', 'r') as f:
    content = f.read()

# Fix the broken regex
content = content.replace(
    '/\\{\\s*\n/',
    '/\\{/'
)

# Also fix it if it appears differently
import re
content = re.sub(r'/\\{\\s\*\s*\n\s*/', r'/\\{/', content)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Regex fixed")
