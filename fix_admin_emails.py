with open('yan-studio.html', 'r') as f:
    content = f.read()

content = content.replace(
    "const ADMIN_EMAILS = ['youngafricansn@gmail.com', 'reganayiecho@gmail.com'];",
    "const ADMIN_EMAILS = ['youngafricansn@gmail.com', 'rayiecho@alustudent.com'];"
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Admin emails fixed")
