with open('yan-studio.html', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'const clean = text.replace' in line and 'json' in line.lower():
        lines[i] = '''    const clean = text.replace(/```json|```/g, '').trim();
    // Extract JSON object robustly
    const jsonMatch = clean.match(/\\{[\\s\\S]*\\}/);
    if (!jsonMatch) throw new Error('No JSON found in response');
    scriptData = JSON.parse(jsonMatch[0]);\n'''
        # Remove the next line that does JSON.parse
        if i+1 < len(lines) and 'JSON.parse' in lines[i+1]:
            lines[i+1] = ''
        print(f"✅ Fixed JSON parsing at line {i+1}")
        break

with open('yan-studio.html', 'w') as f:
    f.writelines(lines)
print("Done")
