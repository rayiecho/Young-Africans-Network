with open('yan-studio.html', 'r') as f:
    content = f.read()

content = content.replace(
    'appId: "1:224204618916:web:yan-studio"',
    'appId: "1:224204618916:web:8ddfd36c6f112b4912fa31"'
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Firebase appId fixed")
