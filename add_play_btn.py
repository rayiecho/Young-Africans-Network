with open('index.html', 'r') as f:
    content = f.read()

old = '        <a href="join.html" class="btn-primary">Join YAN Today</a>\n        <a href="about.html" class="btn-outline">Learn More</a>'

new = '''        <a href="join.html" class="btn-primary">Join YAN Today</a>
        <a href="about.html" class="btn-outline">Learn More</a>
        <button onclick="document.getElementById('yan-video-modal').style.display='flex'" style="background:transparent;border:1.5px solid rgba(255,255,255,0.4);color:#fff;padding:0.85rem 2rem;border-radius:50px;font-size:0.9rem;font-weight:600;cursor:pointer;display:inline-flex;align-items:center;gap:0.6rem;transition:all 0.3s;">
          <span style="width:28px;height:28px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;">▶</span> Watch Our Story
        </button>

<!-- VIDEO MODAL -->
<div id="yan-video-modal" onclick="if(event.target===this)this.style.display='none'" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.92);z-index:9999;align-items:center;justify-content:center;padding:2rem;">
  <div style="position:relative;width:100%;max-width:900px;aspect-ratio:16/9;">
    <button onclick="document.getElementById('yan-video-modal').style.display='none'" style="position:absolute;top:-40px;right:0;background:none;border:none;color:#fff;font-size:1.5rem;cursor:pointer;z-index:10;">✕ Close</button>
    <iframe src="https://share.synthesia.io/embeds/videos/2d2d7cc5-0d31-4d31-9af2-9c2788639f74" loading="lazy" title="YAN Video" allowfullscreen allow="encrypted-media; fullscreen;" style="width:100%;height:100%;border:none;border-radius:12px;"></iframe>
  </div>
</div>'''

updated = content.replace(old, new)

with open('index.html', 'w') as f:
    f.write(updated)

print("✅ Play button and modal added")
