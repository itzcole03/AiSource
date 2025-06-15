#!/usr/bin/env python3
"""
Test script to verify numpy import works from different directories
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def test_numpy_import(working_dir, description):
    """Test if numpy can be imported from a specific directory"""
    print(f"\nTesting {description}:")
    print(f"  Working directory: {working_dir}")    test_script = '''
import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")

try:
    import numpy
    print("SUCCESS: numpy imported successfully")
    print(f"numpy version: {numpy.__version__}")
    print(f"numpy location: {numpy.__file__}")
except Exception as e:
    print(f"FAILED: numpy import error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            cwd=str(working_dir),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"  Exit code: {result.returncode}")
        if result.stdout:
            print("  STDOUT:")
            for line in result.stdout.splitlines():
                print(f"    {line}")
        if result.stderr:
            print("  STDERR:")
            for line in result.stderr.splitlines():
                print(f"    {line}")
                
        return result.returncode == 0
        
    except Exception as e:
        print(f"  ERROR running test: {e}")
        return False

def main():
    """Run numpy import tests"""
    print("=" * 60)
    print("   Numpy Import Test")
    print("=" * 60)
    
    # Find project root
    project_root = Path.cwd()
    while project_root.parent != project_root:
        if (project_root / "frontend" / "dashboard.py").exists():
            break
        project_root = project_root.parent
    else:
        script_dir = Path(__file__).parent
        if (script_dir / "frontend" / "dashboard.py").exists():
            project_root = script_dir
        else:
            print("ERROR: Could not find project root")
            return
    
    print(f"Project root: {project_root}")
    
    # Test from different directories
    tests = [
        (project_root, "Project root directory"),
        (project_root.parent, "Parent of project directory"),
        (project_root / "frontend", "Frontend directory"),
        (Path.home(), "User home directory"),
    ]
    
    # Add temporary directory test
    with tempfile.TemporaryDirectory(prefix="numpy_test_") as temp_dir:
        tests.append((Path(temp_dir), "Temporary directory"))
        
        results = []
        for working_dir, description in tests:
            if working_dir.exists():
                success = test_numpy_import(working_dir, description)
                results.append((description, success))
            else:
                print(f"\nSkipping {description} (directory doesn't exist)")
                results.append((description, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("   Test Results Summary")
    print("=" * 60)
    
    for description, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {status:4} - {description}")
    
    # Recommendation
    print("\n" + "=" * 60)
    print("   Recommendations")
    print("=" * 60)
    
    safe_dirs = [desc for desc, success in results if success]
    unsafe_dirs = [desc for desc, success in results if not success]
    
    if safe_dirs:
        print("  Safe directories for launching Streamlit:")
        for desc in safe_dirs:
            print(f"    - {desc}")
    
    if unsafe_dirs:
        print("  Directories that cause numpy import errors:")
        for desc in unsafe_dirs:
            print(f"    - {desc}")
    
    print("\n  To avoid numpy import errors:")
    print("  1. Always launch Streamlit from a safe directory")
    print("  2. Use absolute paths to the dashboard script")
    print("  3. Set PYTHONPATH if needed to find project modules")

if __name__ == "__main__":
    main()
