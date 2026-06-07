with open('yan-studio.html', 'r') as f:
    content = f.read()

content = content.replace(
    '<div class="main-tabs">',
    '<div class="main-tabs" id="main-tabs">'
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Fixed main-tabs id")
