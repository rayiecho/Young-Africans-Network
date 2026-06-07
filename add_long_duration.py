with open('yan-studio.html', 'r') as f:
    content = f.read()

# Add longer duration options
old = '''              <option value="180">3 minutes</option>'''
new = '''              <option value="180">3 minutes</option>
              <option value="300">5 minutes</option>
              <option value="600">10 minutes</option>
              <option value="900">15 minutes</option>
              <option value="1200">20 minutes</option>'''

content = content.replace(old, new)

# Fix scene count formula for longer videos
old2 = "  const scenes = parseInt(duration) <= 30 ? 3 : parseInt(duration) <= 60 ? 4 : parseInt(duration) <= 90 ? 5 : parseInt(duration) <= 120 ? 6 : 8;"
new2 = "  const scenes = parseInt(duration) <= 30 ? 3 : parseInt(duration) <= 60 ? 4 : parseInt(duration) <= 90 ? 5 : parseInt(duration) <= 120 ? 6 : parseInt(duration) <= 180 ? 8 : parseInt(duration) <= 300 ? 12 : parseInt(duration) <= 600 ? 20 : parseInt(duration) <= 900 ? 28 : 35;"

content = content.replace(old2, new2)

# Fix words per minute calculation
old3 = "  const words = Math.round((parseInt(duration) / 60) * 150);"
new3 = "  const words = Math.round((parseInt(duration) / 60) * 130);"

content = content.replace(old3, new3)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Long duration options added")
