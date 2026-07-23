with open('about.html', 'r', encoding='utf-8') as f:
    content = f.read()

if 'featured-partner-section' in content:
    print("SKIP: about.html already patched")
else:
    teaser = '''<section class="featured-partner-section" style="padding:4rem 2rem;background:var(--light);text-align:center;">
  <p style="font-size:0.78rem;color:var(--red);text-transform:uppercase;letter-spacing:0.1em;font-weight:700;margin-bottom:0.75rem;">Strategic Partnership</p>
  <h2 style="font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;color:var(--navy);margin-bottom:1.25rem;">Proud to Partner With Star9 Freelancer</h2>
  <img src="images/FREELANCE.jpeg" alt="Star9 Freelancer" style="height:70px;width:auto;margin-bottom:1.25rem;border-radius:10px;">
  <p style="max-width:640px;margin:0 auto 1.75rem;color:var(--gray);font-size:0.95rem;line-height:1.7;">
    Star9 Freelancer Ltd equips YAN members with hands-on digital skills and freelancing training, opening doors to remote work and global income opportunities &mdash; at no cost to our members.
  </p>
  <a href="partners.html" style="display:inline-block;background:var(--navy);color:#fff;padding:0.85rem 2rem;border-radius:50px;font-family:Poppins,sans-serif;font-weight:700;font-size:0.85rem;text-decoration:none;">Learn More About This Partnership &rarr;</a>
</section>
<footer>'''
    content = content.replace('<footer>', teaser, 1)
    with open('about.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCHED: about.html teaser section added")
