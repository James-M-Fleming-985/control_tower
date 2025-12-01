#!/usr/bin/env python3
"""
Clean markdown fences from generated code files.
Handles nested fences like ````python containing ```python
"""
import sys
from pathlib import Path


def clean_markdown_fences(file_path: Path) -> tuple[bool, str]:
    """Remove markdown fences from a Python file."""
    try:
        content = file_path.read_text()
        original_lines = content.splitlines()
        
        if not original_lines:
            return False, "Empty file"
        
        # Remove opening fence (first line if it's a fence)
        lines = original_lines[:]
        if lines and lines[0].strip().startswith('```'):
            lines = lines[1:]
            print(f"  ✓ Removed opening fence: {original_lines[0]}")
        
        # Remove closing fence (last line if it's a fence)
        if lines and lines[-1].strip() in ('```', '````'):
            removed = lines[-1]
            lines = lines[:-1]
            print(f"  ✓ Removed closing fence: {removed}")
        
        # Check for any remaining inline fences
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped in ('```', '```python', '```typescript', '```javascript', '```yaml', '````', '````python'):
                print(f"  ✓ Skipped inline fence: {stripped}")
                continue
            cleaned_lines.append(line)
        
        new_content = '\n'.join(cleaned_lines) + '\n'
        
        if new_content != content:
            file_path.write_text(new_content)
            return True, f"Cleaned ({len(original_lines)} → {len(cleaned_lines)} lines)"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {e}"


def main():
    base_dir = Path("/workspaces/control_tower/systems3-project-reporter/FEATURE-WEB-006_PowerPoint_Export")
    
    # Find all implementation.py files
    impl_files = list(base_dir.glob("*/src/implementation.py"))
    
    print(f"Found {len(impl_files)} implementation files\n")
    
    for file in sorted(impl_files):
        print(f"Processing: {file.relative_to(base_dir)}")
        changed, msg = clean_markdown_fences(file)
        print(f"  Result: {msg}\n")
    
    print("✅ All files processed")


if __name__ == "__main__":
    main()
