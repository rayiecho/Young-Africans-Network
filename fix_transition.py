with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'TRANSITION_DURATION' in line:
        lines[i] = "const TRANSITION_DURATION = 250; // ms\n"
        print(f"✅ Transition set to 250ms at line {i+1}")
        break

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)
