with open('yan-studio.html', 'r') as f:
    content = f.read()

# Fix corrupted unicode in math patterns
import re
content = re.sub(
    r'const mathPatterns = \[.*?\];',
    "const mathPatterns = [/\\d+\\s*[\\+\\-\\*\\/\\^]\\s*\\d+/, /=\\s*\\d/, /equation|formula|calculate|solve|theorem/i];",
    content
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Syntax fixed")
