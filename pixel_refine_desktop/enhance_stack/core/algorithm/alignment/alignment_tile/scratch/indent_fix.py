import os

def fix_indentation(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    # lines are 0-indexed. Line 910 is index 909.
    # We need to indent from index 909 to index 1122 (which is line 1123).
    # Line 1124 is @ti_thread (top level), index 1123.
    
    for i, line in enumerate(lines):
        if i >= 909 and i <= 1122:
            # Only add indentation if it's not already indented
            if not line.startswith('    '):
                new_lines.append('    ' + line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(new_lines)
    print("Surgical indentation complete.")

if __name__ == "__main__":
    target_path = r"e:\APP Developer\Pixel Refine\pixel_refine_desktop\enhance_stack\core\algorithm\taichi_algorithm\preprocess.py"
    fix_indentation(target_path)
