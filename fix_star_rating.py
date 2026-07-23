#!/usr/bin/env python3
"""
Fix: 'Continue' button stays disabled on the star-rating step (Step 4).
Adds a missing updateNavState() call inside the star click handler.

Usage:
    python3 fix_star_rating.py path/to/your-file.html
"""

import sys
import shutil

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 fix_star_rating.py path/to/your-file.html")
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    old_block = """            fb.textContent = STAR_LABELS[val];
            fb.classList.add('show');
            setTimeout(()=>fb.classList.remove('show'), 1400);
          };"""

    new_block = """            fb.textContent = STAR_LABELS[val];
            fb.classList.add('show');
            setTimeout(()=>fb.classList.remove('show'), 1400);

            updateNavState();
          };"""

    if old_block not in content:
        print("Could not find the expected code block. "
              "The file may already be patched, or its formatting differs from what was expected.")
        sys.exit(1)

    if content.count(old_block) > 1:
        print("Warning: found multiple matches, aborting to avoid an incorrect edit.")
        sys.exit(1)

    backup_path = filepath + ".bak"
    shutil.copy2(filepath, backup_path)
    print(f"Backup saved to: {backup_path}")

    patched = content.replace(old_block, new_block, 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(patched)

    print(f"Patched successfully: {filepath}")
    print("The 'Continue' button on the ratings step will now enable as soon as a rating is given.")

if __name__ == "__main__":
    main()
