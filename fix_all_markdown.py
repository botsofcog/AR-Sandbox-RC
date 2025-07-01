#!/usr/bin/env python3
"""
Fix All Markdown Issues Script
Automatically fixes all 64 markdown formatting problems
"""

import re
import os
from pathlib import Path

def fix_markdown_file(filepath):
    """Fix all markdown issues in a single file"""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Add blank lines around headings
    # Pattern: heading without blank line before
    content = re.sub(r'\n([^\n].*)\n(#{1,6} )', r'\n\1\n\n\2', content)
    # Pattern: heading without blank line after
    content = re.sub(r'(#{1,6} [^\n]+)\n([^\n#])', r'\1\n\n\2', content)
    
    # Fix 2: Add blank lines around lists
    # Pattern: list without blank line before
    content = re.sub(r'\n([^\n-*+].*)\n([-*+] )', r'\n\1\n\n\2', content)
    # Pattern: list without blank line after
    content = re.sub(r'\n([-*+] [^\n]+)\n([^\n-*+#])', r'\n\1\n\n\2', content)
    
    # Fix 3: Remove trailing spaces
    content = re.sub(r' +\n', '\n', content)
    
    # Fix 4: Fix code blocks without language
    content = re.sub(r'\n```\n', '\n```text\n', content)
    
    # Fix 5: Fix multiple consecutive blank lines
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Fix 6: Ensure file ends with single newline
    content = content.rstrip() + '\n'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {filepath}")

def main():
    """Fix all markdown files"""
    print("🔧 FIXING ALL MARKDOWN ISSUES")
    print("=" * 50)
    
    # List of markdown files to fix
    markdown_files = [
        "README.md",
        "DEPLOYMENT_GUIDE.md", 
        "PROJECT_COMPLETION_SUMMARY.md",
        "FINAL_PROJECT_STATUS.md",
        "TROUBLESHOOTING.md"
    ]
    
    for filepath in markdown_files:
        if Path(filepath).exists():
            fix_markdown_file(filepath)
        else:
            print(f"⚠️ Skipping {filepath} (not found)")
    
    print("\n🎉 ALL MARKDOWN ISSUES FIXED!")
    print("Run diagnostics again to verify.")

if __name__ == "__main__":
    main()
