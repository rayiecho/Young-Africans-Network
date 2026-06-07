with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'max_tokens: 1000' in line:
        lines[i] = line.replace('max_tokens: 1000', 'max_tokens: 4000')
        print(f"✅ max_tokens increased at line {i+1}")

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)
print("Done")
