#!/usr/bin/env python3
"""
Fix Markdown Formatting Issues
Automatically fixes common markdown formatting problems
"""

import re
import os
from pathlib import Path

def fix_markdown_file(file_path):
    """Fix markdown formatting issues in a file"""
    print(f"🔧 Fixing markdown formatting in: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Add blank lines around headings
    # Pattern: heading without blank line after
    content = re.sub(r'(^#{1,6}[^\n]*)\n([^#\n-])', r'\1\n\n\2', content, flags=re.MULTILINE)
    
    # Fix 2: Add blank lines around lists
    # Pattern: list without blank line before
    content = re.sub(r'([^\n])\n(- )', r'\1\n\n\2', content, flags=re.MULTILINE)
    # Pattern: list without blank line after
    content = re.sub(r'(^- [^\n]*)\n([^-\n])', r'\1\n\n\2', content, flags=re.MULTILINE)
    
    # Fix 3: Add blank lines around fenced code blocks
    # Pattern: code block without blank line before
    content = re.sub(r'([^\n])\n(```)', r'\1\n\n\2', content, flags=re.MULTILINE)
    # Pattern: code block without blank line after
    content = re.sub(r'(```[^\n]*)\n([^`\n])', r'\1\n\n\2', content, flags=re.MULTILINE)
    
    # Fix 4: Remove trailing spaces
    content = re.sub(r' +$', '', content, flags=re.MULTILINE)
    
    # Fix 5: Ensure single trailing newline
    content = content.rstrip() + '\n'
    
    # Fix 6: Fix emphasis used as headings (convert ** to ##)
    content = re.sub(r'^\*\*([^*]+)\*\*$', r'## \1', content, flags=re.MULTILINE)
    
    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed formatting issues in: {file_path}")
        return True
    else:
        print(f"ℹ️ No formatting issues found in: {file_path}")
        return False

def main():
    """Fix markdown formatting in all markdown files"""
    print("🔧 AR Sandbox RC - Markdown Formatting Fixer")
    print("=" * 50)
    
    # Find all markdown files
    markdown_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    
    print(f"Found {len(markdown_files)} markdown files to check")
    
    fixed_count = 0
    for file_path in markdown_files:
        try:
            if fix_markdown_file(file_path):
                fixed_count += 1
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    print(f"\n✅ Fixed formatting in {fixed_count} files")
    print("🎉 Markdown formatting cleanup complete!")

if __name__ == "__main__":
    main()
