# 1. Add YAN Studio link to YAN website nav
with open('index.html', 'r') as f:
    content = f.read()

old = '    <li><a href="Entrepreneaurs_Lab.html" style="color:#E63329;font-weight:700;">🧪 Entrepreneurs Lab</a></li>\n  </ul>'
new = '    <li><a href="Entrepreneaurs_Lab.html" style="color:#E63329;font-weight:700;">🧪 Entrepreneurs Lab</a></li>\n    <li><a href="yan-studio.html" style="color:#F5A623;font-weight:700;">🎬 YAN Studio</a></li>\n  </ul>'

content = content.replace(old, new)

# Also add to mobile menu
old_mobile = '  <li><a href="Entrepreneaurs_Lab.html" style="color:#E63329;font-weight:700;">🧪 Entrepreneurs Lab</a></li>\n  <li><a href="join.html" class="mobile-join">Join YAN 🚀</a></li>'
new_mobile = '  <li><a href="Entrepreneaurs_Lab.html" style="color:#E63329;font-weight:700;">🧪 Entrepreneurs Lab</a></li>\n  <li><a href="yan-studio.html" style="color:#F5A623;font-weight:700;">🎬 YAN Studio</a></li>\n  <li><a href="join.html" class="mobile-join">Join YAN 🚀</a></li>'

content = content.replace(old_mobile, new_mobile)

with open('index.html', 'w') as f:
    f.write(content)
print("✅ Added YAN Studio link to index.html nav")

# Also add to all other pages
import os
pages = ['about.html', 'programs.html', 'team.html', 'community.html', 'contact.html', 'events.html', 'gallery.html', 'join.html', 'Journey_Stories.html', 'Entrepreneaurs_Lab.html']
for page in pages:
    if os.path.exists(page):
        with open(page, 'r') as f:
            c = f.read()
        c = c.replace(
            '<li><a href="Entrepreneaurs_Lab.html" style="color:#E63329;font-weight:700;">🧪 Entrepreneurs Lab</a></li>\n  </ul>',
            '<li><a href="Entrepreneaurs_Lab.html" style="color:#E63329;font-weight:700;">🧪 Entrepreneurs Lab</a></li>\n    <li><a href="yan-studio.html" style="color:#F5A623;font-weight:700;">🎬 YAN Studio</a></li>\n  </ul>'
        )
        with open(page, 'w') as f:
            f.write(c)
        print(f"✅ Updated {page}")
