with open('yan-studio.html', 'r') as f:
    content = f.read()

old = '      ${[1,2,3,4,5].map(n => `<button class="star-btn" data-rating="${n}" onclick="document.querySelectorAll(\'.star-btn\').forEach(b=>b.classList.remove(\'selected\'));this.classList.add(\'selected\');document.querySelectorAll(\'.star-btn\').forEach((b,i)=>{if(i<${n})b.style.color=\'#F5A623\';else b.style.color=\'var(--muted)\'})" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>`).join(\'\')}'

new = '''      <button class="star-btn" data-rating="1" onclick="selectStar(1)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>
      <button class="star-btn" data-rating="2" onclick="selectStar(2)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>
      <button class="star-btn" data-rating="3" onclick="selectStar(3)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>
      <button class="star-btn" data-rating="4" onclick="selectStar(4)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>
      <button class="star-btn" data-rating="5" onclick="selectStar(5)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>'''

if old in content:
    content = content.replace(old, new)
    print("✅ Fixed template literal")
else:
    # Find and replace by line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '${[1,2,3,4,5].map' in line:
            lines[i] = '''      <button class="star-btn" data-rating="1" onclick="selectStar(1)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>
      <button class="star-btn" data-rating="2" onclick="selectStar(2)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>
      <button class="star-btn" data-rating="3" onclick="selectStar(3)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>
      <button class="star-btn" data-rating="4" onclick="selectStar(4)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>
      <button class="star-btn" data-rating="5" onclick="selectStar(5)" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>'''
            print(f"✅ Fixed at line {i+1}")
            break
    content = '\n'.join(lines)

# Add selectStar function
content = content.replace(
    'window.openFeedback = function() {',
    '''window.selectStar = function(n) {
    document.querySelectorAll('.star-btn').forEach((b, i) => {
      b.style.color = i < n ? '#F5A623' : 'var(--muted)';
      if (parseInt(b.dataset.rating) === n) b.classList.add('selected');
      else b.classList.remove('selected');
    });
  };

  window.openFeedback = function() {'''
)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("Done")
