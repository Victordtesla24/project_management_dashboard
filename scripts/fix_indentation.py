#!/usr/bin/env python3
import os
import re


def fix_indentation(file_path):
    """Fix closing bracket indentation in a Python file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    fixed_lines = []
    indent_stack = []
    in_multiline = False
    
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        # Skip empty lines
        if not stripped:
            fixed_lines.append(line)
            continue
            
        # Handle multiline strings
        if '"""' in line or "'''" in line:
            in_multiline = not in_multiline
            fixed_lines.append(line)
            continue
            
        if in_multiline:
            fixed_lines.append(line)
            continue
            
        # If line only contains closing brackets/parentheses
        if re.match(r'^[\s)}\]]+$', line):
            # Match indentation with opening bracket
            if indent_stack:
                indent = indent_stack.pop()
            line = ' ' * indent + line.lstrip()
        else:
            # Count opening and closing brackets
            opens = stripped.count('(') + stripped.count('[') + stripped.count('{')
            closes = stripped.count(')') + stripped.count(']') + stripped.count('}')
            
            # Handle line continuation
            if i > 0 and lines[i-1].rstrip().endswith('\\'):
                if not indent_stack:
                    indent_stack.append(indent)
            
            # If there are more opening brackets, store the indentation
            if opens > closes:
                indent_stack.append(indent + 4)
            # If there are more closing brackets, use stored indentation
            elif closes > opens and indent_stack:
                for _ in range(closes - opens):
                    if indent_stack:
                        indent_stack.pop()
                        
            # Handle line continuation ending
            if not line.rstrip().endswith('\\') and indent_stack and \
               i > 0 and lines[i-1].rstrip().endswith('\\'):
                indent_stack.pop()
        
        fixed_lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)

def main():
    """Walk through the project and fix indentation in Python files."""
    for root, _, files in os.walk('.'):
        if '.git' in root or '.venv' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    fix_indentation(file_path)
                    print(f"Fixed indentation in {file_path}")
                except Exception as e:
                    print(f"Error fixing {file_path}: {e}")

if __name__ == '__main__':
    main() 