#!/usr/bin/env python3
"""
CLI interface for Ironclad - AI-powered code generation and verification
"""
import argparse
import sys
import os
from ironclad import main as ironclad_main, DEFAULT_SYSTEM_PROMPT


def load_prompt_file(prompt_file):
    """Load custom system prompt from file"""
    try:
        with open(prompt_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"[!] Error: Prompt file '{prompt_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error reading prompt file '{prompt_file}': {e}")
        sys.exit(1)


def create_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='Generate and verify Python code using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "extract phone numbers from text"
  %(prog)s --model llama3 --output my_bricks "parse JSON data"
  %(prog)s --prompt-file custom.txt "generate sorting algorithm"
        """
    )
    
    parser.add_argument(
        'request',
        help='The programming task or function to generate'
    )
    
    parser.add_argument(
        '--model',
        default=None,
        help='LLM model to use (default: gpt-oss:20b)'
    )
    
    parser.add_argument(
        '--output',
        default=None,
        help='Output directory for verified code (default: verified_bricks)'
    )
    
    parser.add_argument(
        '--prompt-file',
        default=None,
        help='File containing custom system prompt'
    )
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Load custom prompt if specified
    system_prompt = DEFAULT_SYSTEM_PROMPT
    if args.prompt_file:
        system_prompt = load_prompt_file(args.prompt_file)
        print(f"[*] Using custom prompt from: {args.prompt_file}")
    
    # Call ironclad main with parameters
    try:
        ironclad_main(
            request=args.request,
            model_name=args.model,
            output_dir=args.output,
            system_prompt=system_prompt
        )
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()