#!/usr/bin/env python3
"""
Fix syntax errors in dashboard.py
"""

import re

def fix_dashboard_syntax():
    """Fix missing newlines in dashboard.py"""
    file_path = "frontend/dashboard.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the pattern: }    def function_name
    pattern1 = r'(\}\s*)(def\s+\w+)'
    content = re.sub(pattern1, r'\1\n    \2', content)
    
    # Fix the pattern: }        except Exception
    pattern2 = r'(\}\s*)(except\s+)'
    content = re.sub(pattern2, r'\1\n        \2', content)
    
    # Fix the pattern: "text"        except Exception
    pattern3 = r'(\"[^\"]*\")\s+(except\s+)'
    content = re.sub(pattern3, r'\1\n        \2', content)
    
    # Fix general pattern of missing newlines before statements
    pattern4 = r'(\w+)\s+(except\s+)'
    content = re.sub(pattern4, r'\1\n        \2', content)
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed syntax errors in dashboard.py")

if __name__ == "__main__":
    fix_dashboard_syntax()
