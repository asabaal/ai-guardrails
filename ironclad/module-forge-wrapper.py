#!/usr/bin/env python3
"""
Simple module forge wrapper that handles imports properly
"""
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python module-forge-wrapper.py 'Create a CLI tool that...'")
        sys.exit(1)
    
    request = sys.argv[1]
    
    import module_forge
    
    # Simulate command line args for module_forge
    sys.argv = ['module_forge', request]
    module_forge.main()

if __name__ == "__main__":
    main()