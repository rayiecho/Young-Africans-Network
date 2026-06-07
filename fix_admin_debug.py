with open('yan-studio.html', 'r') as f:
    content = f.read()

content = content.replace(
    '      if (ADMIN_EMAILS.includes(user.email)) showAdminTab();',
    '      console.log("Logged in as:", user.email);\n      console.log("Is admin:", ADMIN_EMAILS.includes(user.email));\n      if (ADMIN_EMAILS.includes(user.email)) showAdminTab();'
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Debug added")
