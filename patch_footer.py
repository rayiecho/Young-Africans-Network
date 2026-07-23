FILES = ["Entrepreneaurs_Lab.html","Journey_Stories.html","about.html","contact.html",
         "events.html","gallery.html","index.html","join.html","login.html",
         "profile.html","programs.html","register.html","team.html"]

PARTNER_BLOCK = '''<footer>
  <div style="max-width:1200px;margin:0 auto 2rem;text-align:center;">
    <p style="font-size:0.7rem;color:rgba(255,255,255,0.45);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.85rem;font-weight:600;">In Partnership With</p>
    <a href="partners.html" style="display:inline-block;">
      <img src="images/FREELANCE.jpeg" alt="Star9 Freelancer - YAN Partner" style="height:44px;width:auto;border-radius:8px;background:#fff;padding:6px 14px;">
    </a>
  </div>
'''

for fname in FILES:
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("SKIP (not found): " + fname)
        continue
    if 'In Partnership With' in content:
        print("SKIP (already patched): " + fname)
        continue
    if '<footer>' not in content:
        print("SKIP (no <footer> tag): " + fname)
        continue
    new_content = content.replace('<footer>', PARTNER_BLOCK, 1)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("PATCHED: " + fname)
