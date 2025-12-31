#!/usr/bin/env python3
"""
Test ironclad functionality
"""
import sys
import os
import importlib.util

# Load modules manually to avoid import issues
spec = importlib.util.spec_from_file_location("code_utils", "src/code_utils.py")
code_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_utils)

spec = importlib.util.spec_from_file_location("ironclad", "src/ironclad.py")
ironclad = importlib.util.module_from_spec(spec)

# Monkey patch the imports
ironclad.clean_json_response = code_utils.clean_json_response
ironclad.clean_code_content = code_utils.clean_code_content

spec.loader.exec_module(ironclad)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ironclad.py 'request description'")
        sys.exit(1)
    
    request = sys.argv[1]
    ironclad.main(request=request)