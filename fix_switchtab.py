with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "['create','enhance','library'].forEach(t => {" in line and i > 3000:
        lines[i] = "  ['create','enhance','library','photo'].forEach(t => {\n"
        print(f"✅ Fixed switchTab at line {i+1}")
        break

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)
