#!/usr/bin/env python3
"""
Entry point scripts for Ironclad tools
"""
#!/usr/bin/env python3
"""
Entry point script for Ironclad CLI
"""
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

if __name__ == "__main__":
    import ironclad
    
    # Parse command line args
    if len(sys.argv) < 2:
        print("Usage: python ironclad-cli.py 'request description'")
        sys.exit(1)
    
    request = sys.argv[1]
    model_name = None
    output_dir = None
    
    ironclad.main(request=request, model_name=model_name, output_dir=output_dir)