with open('yan-studio.html', 'r') as f:
    content = f.read()

# Move admin check to after DOM loads in main script
old = '      console.log("Logged in as:", user.email);\n      console.log("Is admin:", ADMIN_EMAILS.includes(user.email));\n      if (ADMIN_EMAILS.includes(user.email)) showAdminTab();'

new = '''      console.log("Logged in as:", user.email);
      console.log("Is admin:", ADMIN_EMAILS.includes(user.email));
      if (ADMIN_EMAILS.includes(user.email)) {
        // Small delay to ensure DOM is ready
        setTimeout(() => showAdminTab(), 500);
      }'''

content = content.replace(old, new)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Fixed")
