with open('index.html', 'r') as f:
    content = f.read()

old = '<!-- HERO -->\n<section class="hero">'

new = '''<!-- HERO -->
<section class="hero" style="position:relative;">
  <!-- VIDEO BACKGROUND -->
  <div style="position:absolute;inset:0;z-index:0;overflow:hidden;">
    <div style="position:relative;overflow:hidden;width:100%;height:100%;">
      <iframe src="https://share.synthesia.io/embeds/videos/2d2d7cc5-0d31-4d31-9af2-9c2788639f74" loading="lazy" title="YAN Video" allowfullscreen allow="encrypted-media; fullscreen;" style="position:absolute;width:100%;height:100%;top:0;left:0;border:none;padding:0;margin:0;overflow:hidden;object-fit:cover;pointer-events:none;"></iframe>
    </div>
    <!-- Dark overlay so text stays readable -->
    <div style="position:absolute;inset:0;background:rgba(10,18,60,0.82);z-index:1;"></div>
  </div>'''

updated = content.replace(old, new)

# Make sure hero-inner is above the video
updated = updated.replace(
    '<div class="hero-inner">',
    '<div class="hero-inner" style="position:relative;z-index:2;">',
    1
)

with open('index.html', 'w') as f:
    f.write(updated)

print("✅ Video background added to hero")
