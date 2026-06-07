with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'const mathPatterns' in line:
        lines[i] = "  const mathPatterns = [/equation|formula|calculate|solve|theorem/i];\n"
        print(f"✅ Fixed line {i+1}")
        break

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)
print("Done")
