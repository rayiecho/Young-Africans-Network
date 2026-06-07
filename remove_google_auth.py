with open('yan-studio.html', 'r') as f:
    content = f.read()

# Remove both Google sign-in buttons
import re
content = re.sub(
    r'<div style="margin-top:0\.75rem;">\s*<button onclick="signInGoogle\(\)".*?</button>\s*</div>',
    '',
    content,
    flags=re.DOTALL
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Google auth removed")
