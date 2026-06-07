with open('yan-studio.html', 'r') as f:
    content = f.read()

content = content.replace(
    "const ADMIN_EMAILS = ['youngafricansn@gmail.com', 'rayiecho@alustudent.com'];",
    "const ADMIN_EMAILS = ['youngafricansn@gmail.com', 'r.ayiecho@alustudent.com'];"
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Admin email fixed to r.ayiecho@alustudent.com")
